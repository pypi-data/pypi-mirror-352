from dataclasses import dataclass, field
from typing import Dict, Optional, Iterable, Union as PyUnion, Tuple, cast
from datetime import date, datetime
import networkx as nx

from relationalai.early_access.metamodel import ir, types, visitor, helpers
from relationalai.early_access.metamodel.util import OrderedSet, ordered_set

# TODO: Simplify TypeVar so it does not contain constraint information
@dataclass
class TypeVar:
    """A type variable."""
    # The node that this type variable is bound to.
    # Here this is always a Var or a Field.
    # Together with the context and index, this uniquely identifies the type variable.
    node: PyUnion[ir.Field, ir.Var] = field(init=True)

    # When a type variable represents a tuple type, this is the index of the tuple element, or -1.
    index: int = field(init=True)

    # This is the enclosing lookup or aggregate node being applied.
    # The context is used to distinguish type variables for a Field at each use of the Field.
    context: PyUnion[ir.Lookup, ir.Aggregate, ir.Rank, None] = field(init=True)

    # The upper bound of the type variable.
    upper_bound: OrderedSet[ir.Type] = field(default_factory=OrderedSet, init=False, compare=False, hash=False, repr=False)
    # The lower bound of the type variable.
    lower_bound: OrderedSet[ir.Type] = field(default_factory=OrderedSet, init=False, compare=False, hash=False, repr=False)
    # Set of TypeVars that are supertypes of this type variable.
    node_super_types: OrderedSet["TypeVar"] = field(default_factory=OrderedSet, init=False, compare=False, hash=False, repr=False)
    # Inverse of node_super_types.
    node_sub_types: OrderedSet["TypeVar"] = field(default_factory=OrderedSet, init=False, compare=False, hash=False, repr=False)

    # Union-find data structure.
    # The rank of the type variable.
    rank: int = field(default=1, init=False, compare=False, hash=False, repr=False)
    # The next type variable in the union-find data structure. If this is None, the type variable is the root of its union-find tree.
    next: Optional["TypeVar"] = field(default=None, init=False, compare=False, hash=False, repr=False)

    def __hash__(self) -> int:
        return hash((self.node.id, self.index, self.context.id if self.context else None))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, TypeVar):
            return False
        if self.node.id == other.node.id and self.index == other.index:
            if self.context and other.context:
                return self.context.id == other.context.id
            else:
                return self.context is None and other.context is None
        return False

    def __str__(self) -> str:
        base = TypeVar.pretty_name(self.node, self.index, self.context, lowercase=True)
        return f"{base} (id={self.node.id})"

    def find(self) -> "TypeVar":
        """Find the root of this type variable and perform path compression."""
        if self.next is None:
            return self
        self.next = self.next.find()
        return self.next

    def canonical_repr(self) -> "TypeVar":
        return self.find()

    def is_canonical(self) -> bool:
        return self.find() == self

    def union(self, other: "TypeVar") -> "TypeVar":
        """Union this type variable with another, returning the root of the union."""
        top = self.find()
        bot = other.find()
        assert top.next is None
        assert bot.next is None
        if top == bot:
            return top

        # But the lower rank tree is under the higher rank tree.
        if top.rank < bot.rank:
            top, bot = bot, top

        # For more consistent debugging output,
        # prefer that the root be a global field rather than a var,
        # and prefer global fields to instantiated fields.
        if isinstance(bot.node, ir.Field) and bot.context:
            top, bot = bot, top
        if isinstance(top.node, ir.Field) and not top.context:
            top, bot = bot, top

        # But bot under top.
        bot.next = top
        top.rank += bot.rank

        # Union bot's data into top.
        top.upper_bound.update(bot.upper_bound)
        top.lower_bound.update(bot.lower_bound)
        top.node_super_types.update(bot.node_super_types)
        top.node_sub_types.update(bot.node_sub_types)

        # Clear bot.
        bot.upper_bound.clear()
        bot.lower_bound.clear()
        bot.node_super_types.clear()
        bot.node_sub_types.clear()


        assert self.find() is top
        assert other.find() is top
        return top

    def compute_type(self) -> ir.Type:
        root = self.find()

        upper = types.compute_lowest_bound(root.upper_bound)
        lower = types.compute_highest_bound(root.lower_bound)

        if lower and upper:
            lower = types.intersect(lower, upper)

        if lower:
            return cast(ir.Type, lower)

        if upper:
            return cast(ir.Type, upper)

        return cast(ir.Type, types.Any)

    @staticmethod
    def pretty_name(node: ir.Node, index: int, context: Optional[ir.Node], lowercase: bool=False, short: bool=False) -> str:
        if short:
            if isinstance(node, ir.Var):
                return f"`{node.name}`"
            elif isinstance(node, ir.Field):
                if index < 0:
                    return f"`{node.name}`"
                else:
                    return f"{'e' if lowercase else 'E'}lement {index+1} of `{node.name}`"
            else:
                raise ValueError(f"pretty_name: unexpected node type {type(node)}")
        else:
            if isinstance(node, ir.Var):
                return f"var `{node.name}`"
            elif isinstance(node, ir.Field):
                name = node.name
                if isinstance(context, ir.Lookup):
                    name = f"{context.relation.name}.{name}"
                    prefix = "access"
                    lowercase = True
                elif isinstance(context, ir.Aggregate):
                    name = f"{context.aggregation.name}.{name}"
                    prefix = "access"
                    lowercase = True
                elif isinstance(context, ir.Rank):
                    name = "rank"
                    prefix = "access"
                    lowercase = True
                elif isinstance(context, ir.Relation):
                    name = f"{context.name}.{name}"
                    prefix = "field"
                elif not context:
                    prefix = "field"
                else:
                    raise ValueError(f"pretty_name: unexpected context type {type(context)}")

                if index < 0:
                    return f"{prefix} `{name}`"
                else:
                    return f"element {index+1} of {prefix} `{name}`"
            else:
                raise ValueError(f"pretty_name: unexpected node type {type(node)}")

@dataclass
class TypeError:
    """A type inference error."""
    msg: str
    node: ir.Node

    def __hash__(self):
        return hash((self.msg, self.node.id))

    def __eq__(self, other):
        return self.msg == other.msg and self.node.id == other.node.id

Typeable = PyUnion[ir.Value, ir.Type, ir.Var, ir.Field, TypeVar]

@dataclass
class TypeEnv:
    """Environment for type inference that tracks type bounds for each node."""

    # The model being type-checked.
    model: ir.Model

    # Diagnostics. For now, this is just strings.
    diags: OrderedSet[TypeError]

    # Maps node ids (and tuple index, as needed) to the type variables for their types.
    type_vars: Dict[Tuple[int, int, int], TypeVar]

    # How verbose to be with debug info, 0 for off.
    verbosity: int

    # Should we perform stricter checks on the inferred types.
    strict: bool

    def __init__(self, model: ir.Model, strict: bool, verbosity: int=0):
        super().__init__()
        self.model = model
        self.diags = OrderedSet[TypeError]()
        self.type_vars = {}
        self.strict = strict
        self.verbosity = verbosity

    def _complain(self, node: ir.Node, msg: str):
        """Report an error."""
        self.diags.add(TypeError(msg, node))

    def get_type_var(self, node: PyUnion[ir.Field, ir.Var], index: int = -1, context: PyUnion[ir.Lookup, ir.Aggregate, ir.Rank, None] = None) -> TypeVar:
        key = (node.id, index, context.id if context else node.id)
        if key not in self.type_vars:
            self.type_vars[key] = TypeVar(node, index, context)
        tv = self.type_vars[key]
        # TODO: Why does this sometimes fail?
        # assert tv.node == node, f"TypeVar {tv}, {tv.node} does not match node {node}"
        assert tv.index == index
        return tv

    def find_type_var(self, node: PyUnion[ir.Field, ir.Var], index: int = -1, context: PyUnion[ir.Lookup, ir.Aggregate, ir.Rank, None] = None) -> TypeVar:
        tv = self.get_type_var(node, index, context)
        return tv.find()

    def _get_type(self, t: PyUnion[ir.Literal, ir.PyValue]) -> ir.Type:
        if isinstance(t, str):
            return types.String
        elif isinstance(t, bool):
            return types.Bool
        elif isinstance(t, int):
            return types.Int
        elif isinstance(t, float):
            return types.Float
        # Note that the check for datetime must be before date since datetime <: date
        elif isinstance(t, datetime):
            return types.DateTime
        elif isinstance(t, date):
            return types.Date
        elif isinstance(t, ir.Literal):
            return t.type
        else:
            raise ValueError(f"Unexpected value {t} of type {type(t)}")

    def add_bound(self, lower: Typeable, upper: Typeable) -> None:
        lower_t = self._type_or_typevar(lower)
        upper_t = self._type_or_typevar(upper)
        self._add_bound(lower_t, upper_t)

    def _add_bound(self, lower: PyUnion[ir.Type, TypeVar], upper: PyUnion[ir.Type, TypeVar]):
        if isinstance(upper, ir.UnionType):
            for t in upper.types:
                self.add_bound(lower, t)
        elif isinstance(lower, ir.UnionType):
            for t in lower.types:
                self.add_bound(t, upper)
        elif isinstance(lower, ir.Type) and isinstance(upper, ir.Type):
            if lower == upper:
                return
            elif types.is_subtype(lower, upper):
                return
            else:
                self._complain(lower, f"Type {ir.type_to_string(lower)} is not a subtype of {ir.type_to_string(upper)}")
        elif isinstance(lower, ir.Type) and isinstance(upper, TypeVar):
            if not types.is_null(lower):
                upper.find().lower_bound.add(lower)
        elif isinstance(lower, TypeVar) and isinstance(upper, ir.Type):
            if not types.is_any(upper):
                lower.find().upper_bound.add(upper)
        else:
            assert isinstance(lower, TypeVar) and isinstance(upper, TypeVar), f"Unexpected types {type(lower)} and {type(upper)}"
            lower.find().node_super_types.add(upper.find())
            upper.find().node_sub_types.add(lower.find())

    def add_equality(self, t1: Typeable, t2: Typeable) -> None:
        tt1 = self._type_or_typevar(t1)
        tt2 = self._type_or_typevar(t2)
        self._add_equality(tt1, tt2)

    def _type_or_typevar(self, t: Typeable) -> PyUnion[ir.Type, TypeVar]:
        if t is None:
            return types.Null
        elif isinstance(t, (ir.Literal, str, bool, int, float, date, datetime)):
            return self._get_type(t)
        elif isinstance(t, (ir.Var, ir.Field)):
            return self.get_type_var(t)
        elif isinstance(t, tuple):
            return types.AnyList
        else:
            assert isinstance(t, ir.Type) or isinstance(t, TypeVar), f"Unexpected type {type(t)}"
            return t

    def _add_equality(self, t1: PyUnion[ir.Type, TypeVar], t2: PyUnion[ir.Type, TypeVar]):
        if isinstance(t1, ir.Type) and isinstance(t2, ir.Type):
            self.add_bound(t1, t2)
            self.add_bound(t2, t1)
        elif isinstance(t1, ir.Type) and isinstance(t2, TypeVar):
            # Add t1 as both a lower and upper bound of t2.
            if not types.is_any(t1):
                t2.find().upper_bound.add(t1)
            if not types.is_null(t1):
                t2.find().lower_bound.add(t1)
        elif isinstance(t1, TypeVar) and isinstance(t2, ir.Type):
            self._add_equality(t2, t1)
        else:
            assert isinstance(t1, TypeVar) and isinstance(t2, TypeVar)
            tt1 = t1.find()
            tt2 = t2.find()

            if tt1 != tt2:
                # Check that two type variables have compatible bounds.
                for lb in tt1.lower_bound:
                    for ub in tt2.upper_bound:
                        # TODO: why is that Not added?
                        if not types.is_subtype(lb, ub) and not types.is_subtype(ub, lb):
                            self._complain(t1.node, f"The types of {t1} and {t2} are not compatible: {ir.type_to_string(lb)} <: {t1}, but {t2} <: {ir.type_to_string(ub)}")
                for lb in tt2.lower_bound:
                    for ub in tt1.upper_bound:
                        # TODO: why is that Not added?
                        if not types.is_subtype(lb, ub) and not types.is_subtype(ub, lb):
                            self._complain(t2.node, f"The types of {t2} and {t1} are not compatible: {ir.type_to_string(lb)} <: {t2}, but {t1} <: {ir.type_to_string(ub)}")

                tt1.union(tt2)

    def dump(self, as_dot: bool=False):
        result = ""

        def _dump_title(title: str) -> str:
            if as_dot:
                return ""
            else:
               return f"\n{title}\n"

        def _dump_bound(lower: Typeable, upper: Typeable) -> str:
            if isinstance(lower, ir.Type):
                lower = ir.type_to_string(lower)
            if isinstance(upper, ir.Type):
                upper = ir.type_to_string(upper)

            if as_dot:
                return f"\t\"{lower}\" -> \"{upper}\"\n"
            else:
                return f"\t{lower} <: {upper}\n"

        def _dump_equality(t1: TypeVar, t2: TypeVar) -> str:
            if as_dot:
                return f"\t\"{t1}\" -> \"{t2}\" [dir=both, arrowtail=none, arrowhead=none, color=blue];\n"
            else:
                return f"\t{t1} == {t2}\n"

        # Match with the canonical representations
        result += _dump_title("Type vars:")
        for v in self._tyvars():
            if not v.is_canonical():
                result += _dump_equality(v, v.canonical_repr())

        # Match with the upper bound type vars
        result += _dump_title("Upper bound type vars:")
        for v in self._tyvars():
            if not v.is_canonical():
                continue
            for w in v.node_super_types:
                result += _dump_bound(v, w)

        # Match with the upper and lower type bounds
        result += _dump_title("Bounds for type vars:")
        for v in self._tyvars():
            if not v.is_canonical():
                continue
            if v.lower_bound:
                for typ in v.lower_bound:
                    result += _dump_bound(typ, v)
            if v.upper_bound:
                for typ in v.upper_bound:
                    result += _dump_bound(v, typ)

        if as_dot:
            result = "digraph G {\n" +\
                "\tnode [shape=box];\n" +\
                result +\
                "}"
        print(result)

    def _collapse_node_supertype_cycles(self):
        # Create a directed graph from the node_super_types relationships
        G = nx.DiGraph()

        for v in self._tyvars():
            v = v.find()
            for w in v.node_super_types:
                w = w.find()
                G.add_edge(v, w)

        # Equate all type vars in the same SCC.
        for scc in nx.strongly_connected_components(G):
            if len(scc) > 1:
                cycle = list(scc)
                for t in cycle[1:]:
                    cycle[0].union(t)

    def type_bounds_compatible(self, tv1: TypeVar, tv2: TypeVar) -> bool:
        # Check that two type variables have compatible bounds.
        for lb in tv1.lower_bound:
            for ub in tv2.upper_bound:
                if not types.is_subtype(lb, ub):
                    return False
        for lb in tv2.lower_bound:
            for ub in tv1.upper_bound:
                if not types.is_subtype(lb, ub):
                    return False
        return True

    def compute_type(self, tv: TypeVar, node: PyUnion[ir.Var, ir.Field], index: int, parent: Optional[ir.Node]) -> ir.Type:
        root = tv.find()

        t = root.compute_type()

        if types.is_null(t):
            upper = types.compute_lowest_bound(root.upper_bound)
            lower = types.compute_highest_bound(root.lower_bound)
            name = TypeVar.pretty_name(node, index, parent, lowercase=True)
            short_name = TypeVar.pretty_name(node, index, parent, lowercase=True, short=True)
            if lower and upper and not types.is_subtype(lower, upper):
                self._complain(node, f"Inferred an empty type for {name}: {ir.type_to_string(lower)} <: type({short_name}) <: {ir.type_to_string(upper)}.")
            else:
                self._complain(node, f"Inferred an empty type for {name}.")

        # We don't have any constraints that bound the type from above.
        # This means we should infer the type as Any, which is not useful.
        if self.strict and types.is_any(t):
            name = TypeVar.pretty_name(node, index, parent, lowercase=True)
            self._complain(node, f"Could not infer a type for {name} more specific than Any. This probably means ")

        return t

    def _propagate_bounds(self):
        """Propagate bounds along node_super_types edges until a fixpoint is reached."""

        worklist = ordered_set(*self._tyvars())
        while worklist:
            sub = worklist.pop()
            sub = sub.find()
            for sup in sub.node_super_types:
                sup = sup.find()
                if sup.upper_bound:
                    # Propagate upper bounds downward from supertype to subtype.
                    # We only need to propagate upper bounds downward if they are more precise.
                    # That is, if we have sub <: Number --> sup <: Int, we propagate the Int downward.
                    bound = []
                    for t in sup.upper_bound:
                        if any(types.is_proper_subtype(t, u) for u in sub.upper_bound):
                            bound.append(t)
                    if bound:
                        if self.verbosity > 2:
                            print(f"Unioning upper bound of {sub} with {sup} ub={ir.types_to_string(bound)}")
                            print(f" - old ub={ir.types_to_string(sub.upper_bound)}")
                            print(f" - new ub={ir.types_to_string(sub.upper_bound | bound)}")
                        n = len(sub.upper_bound)
                        sub.upper_bound |= bound
                        if n != len(sub.upper_bound):
                            worklist.add(sub)
                if sub.lower_bound:
                    # Propagate lower bounds upward from subtype to supertype.
                    # We only need to propagate lower bounds upward if they are more precise.
                    # That is, if we have Int :> sub --> Number :> sup, we propagate the Int upward.
                    bound = []
                    for t in sub.lower_bound:
                        if any(types.is_proper_subtype(u, t) for u in sub.lower_bound):
                            bound.append(t)
                    if bound:
                        if self.verbosity > 2:
                            print(f"Unioning lower bound of {sup} with {sub} lb={ir.types_to_string(bound)}")
                            print(f" - old lb={ir.types_to_string(sup.lower_bound)}")
                            print(f" - new lb={ir.types_to_string(sup.lower_bound | bound)}")
                        n = len(sup.lower_bound)
                        sup.lower_bound |= bound
                        if n != len(sup.lower_bound):
                            worklist.add(sup)

    def _tyvars(self) -> Iterable[TypeVar]:
        """Return all the type variables in the graph."""
        return self.type_vars.values()

    def _equivalent_tyvars(self, tv: TypeVar) -> Iterable[TypeVar]:
        """Return the set of type variables that are equivalent to the given type variable."""
        tv = tv.find()
        return [v for v in self._tyvars() if v.find() == tv]

    def _unify_instantiated_relations(self):
        v = UnifyInstantiatedRelations(self)
        self.model.accept(v)
        return v.changed

    def solve(self):
        """Solve the type constraints."""

        if self.verbosity:
            print("\n")
            if self.verbosity > 1:
                ir.dump(self.model)
            else:
                print(self.model)

            print("\n")
            print("Constraints before solving:")

            self.dump()

        # Collapse all the node_super_types cycles into equalities.
        self._collapse_node_supertype_cycles()
        # Propagate bounds.
        self._propagate_bounds()

        # Equate instantiated relations with their non-instantiated counterparts.
        while self._unify_instantiated_relations():
            # TODO This should be done incrementally on the new equivalent relations in the worklist.
            self._collapse_node_supertype_cycles()
            self._propagate_bounds()

        if self.verbosity:
            print("\n")
            print("Constraints after solving:")
            self.dump()

@dataclass
class UnifyInstantiatedRelations(visitor.Visitor):
    """
    Unify instantiated relations to their global counterparts.

    Consider the lookup R(a, b).

    Where R is defined as:
        R(x: Any, y: Any)
            overload R(x1: Int, y1: Int)
            overload R(x2: String, y2: String)

    We consider each variable and field to be a type variable.
    Fields without a context are "global" fields. Fields with a context are "instantiated" fields.
    We introduced type variables x' and y' for the instantiated fields of R at this lookup.
    The instantiated field type variables are created using the Lookup as the context;
    for instance, x' is env.get_type_var(x, context="lookup R(a, b)")

    CollectTypeConstraints should have added the following constraints:
        a = x'   # arguments of a lookup must match the instantiated fields
        b = y'
        x' <: x  # instantiated fields are subtypes of the global fields
        y' <: y
        x <: Any # declared type of the global fields
        y <: Any

    At this point, we would like to choose the overload that matches R.

    Suppose x'.compute_type() = Int.
    In this case, we search the overloads of R for one that matches and add the additional constraints:
        x' <: x1
        y' <: y1
    Adding these constraints will allow us to infer also that y'.compute_type() is also Int.

    Later, the ReconcileOverloads rewrite will replace the abstract relation R(x: Any, y: Any)
    used at the lookup with the concrete overload R(x1: Int, y1: Int).
    """
    env: TypeEnv = field(init=True)
    changed: bool = field(default=False)

    def computed_fields(self, relation: ir.Relation, context: PyUnion[ir.Lookup, ir.Aggregate, ir.Rank]) -> list[ir.Field]:
        computed_fields = []
        for f in relation.fields:
            if isinstance(f.type, ir.TupleType):
                fts = list(f.type.types)
                tvs = [self.env.get_type_var(f, i, context=context).find() for i in range(len(fts))]
                ts = [tv.compute_type() for tv in tvs]
                ts = [types.intersect(t, ft) for t, ft in zip(ts, fts)]
                t = ir.TupleType(tuple(ts))
            else:
                ft = f.type
                tv = self.env.get_type_var(f, context=context).find()
                t = tv.compute_type()
                t = types.intersect(t, ft)
            f2 = f.reconstruct(type=t)
            computed_fields.append(f2)
        return computed_fields

    def find_matching_relation(self, abstract_relation: ir.Relation, context: PyUnion[ir.Lookup, ir.Aggregate, ir.Rank]):
        """
        Find a relation with the same name and type signature that doesn't have a instantiated annotation.
        """
        # Find any overloads that might match the computed instantiated field types so far.
        # Now check if the computed types match.
        candidates = []
        for overload in abstract_relation.overloads:
            compatible = True
            for f1, f2 in zip(overload.fields, abstract_relation.fields):
                # This is complicated by the second-class handling of tuple types.
                if isinstance(f1.type, ir.TupleType) and isinstance(f2.type, ir.TupleType):
                    assert len(f1.type.types) == len(f2.type.types)
                    fts1 = list(f1.type.types)
                    fts2 = list(f2.type.types)
                    tvs1 = [self.env.get_type_var(f1, i).find() for i in range(len(fts1))]
                    tvs2 = [self.env.get_type_var(f2, i, context=context).find() for i in range(len(fts2))]
                else:
                    fts1 = [f1.type]
                    fts2 = [f2.type]
                    tvs1 = [self.env.get_type_var(f1).find()]
                    tvs2 = [self.env.get_type_var(f2, context=context).find()]

                for tv1, tv2, ft1, ft2 in zip(tvs1, tvs2, fts1, fts2):
                    if tv1 == tv2:
                        # Already equal.
                        continue
                    t1 = tv1.compute_type()
                    t2 = tv2.compute_type()
                    if not types.matches(t1, ft1):
                        if self.env.verbosity > 2:
                            print(f"Type mismatch: {ir.type_to_string(t1)} != {ir.type_to_string(ft1)}")
                        compatible = False
                        break
                    if not types.matches(t2, ft2):
                        if self.env.verbosity > 2:
                            print(f"Type mismatch: {ir.type_to_string(t2)} != {ir.type_to_string(ft2)}")
                        compatible = False
                        break
                    t1 = types.intersect(t1, ft1)
                    t2 = types.intersect(t2, ft2)
                    if not types.matches(t1, t2):
                        # Types don't match.
                        if self.env.verbosity > 2:
                            print(f"Types don't match: {ir.type_to_string(t1)} != {ir.type_to_string(t2)}")
                        compatible = False
                        break
                    else:
                        if self.env.verbosity > 2:
                            print(f"Types match: {tv1} ~ {tv2}")
                            print(f"Types match: {ir.type_to_string(t1)} ~ {ir.type_to_string(t2)}")
                    if not self.env.type_bounds_compatible(tv1, tv2):
                        # Bounds don't match.
                        if self.env.verbosity > 2:
                            print(f"Bounds don't match: {tv1} != {tv2}")
                        compatible = False
                        break
                if not compatible:
                    break

            if compatible:
                candidates.append(overload)
                if self.env.verbosity > 2:
                    print(f"Found candidate {overload} for {abstract_relation}")
            else:
                if self.env.verbosity > 2:
                    print(f"Not compatible: {overload} for {abstract_relation}")

        if len(candidates) > 1:
            # If there are multiple candidates, choose the most specific one.
            maximal_candidates = []
            for candidate in candidates:
                if not any(helpers.relation_is_proper_subtype(other, candidate) for other in candidates):
                    maximal_candidates.append(candidate)
            candidates = maximal_candidates

        if len(candidates) == 0:
            computed_types = [f.type for f in self.computed_fields(abstract_relation, context)]
            self.env._complain(abstract_relation, f"Relation `{abstract_relation.name}` (id={abstract_relation.id}) has no matching relation with types ({ir.types_to_string(computed_types)}).")
            return None
        elif len(candidates) == 1:
            # There is exactly one matching overload.
            # Equate the instantiated fields of the lookup with the global fields of the overload.
            overload = candidates[0]
            if self.env.verbosity > 2:
                print(f"Found matching relation {overload} for {abstract_relation}")
                print("\n\nENV before merging\n\n")
                self.env.dump()
                print("\n")
                print(f"Found matching relation {overload} for {abstract_relation}")
            for f1, f2 in zip(overload.fields, abstract_relation.fields):
                if isinstance(f1.type, ir.TupleType) and isinstance(f2.type, ir.TupleType):
                    assert len(f1.type.types) == len(f2.type.types)
                    tvs1 = [self.env.get_type_var(f1, i).find() for i in range(len(f1.type.types))]
                    tvs2 = [self.env.get_type_var(f2, i, context=context).find() for i in range(len(f2.type.types))]
                else:
                    tvs1 = [self.env.get_type_var(f1).find()]
                    tvs2 = [self.env.get_type_var(f2, context=context).find()]
                for tv1, tv2 in zip(tvs1, tvs2):
                    if tv1 != tv2:
                        self.env.add_equality(tv1, tv2)
                        self.changed = True
            if self.env.verbosity > 2:
                print("\n\nENV after merging\n\n")
                self.env.dump()
                print("\n")
        else:
            assert len(candidates) > 1
            # For now, if there are multiple candidates, just continue.
            # A later pass might narrow down the candidates.
            # self.env._complain(relation, f"Relation `{relation.name}` (id={relation.id}) has multiple matching relations.")
            pass

    def visit_lookup(self, node: ir.Lookup, parent: Optional[ir.Node]):
        if node.relation.overloads:
            self.find_matching_relation(node.relation, node)

        super().visit_lookup(node, parent)

    def visit_aggregate(self, node: ir.Aggregate, parent: Optional[ir.Node]):
        if node.aggregation.overloads:
            self.find_matching_relation(node.aggregation, node)
        super().visit_aggregate(node, parent)
