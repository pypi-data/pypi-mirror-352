"""
Type inference for the IR.
"""
from dataclasses import dataclass, field
from typing import Dict, Optional, Union as PyUnion, Tuple
import os

from relationalai.early_access.metamodel.util import OrderedSet, ordered_set
from relationalai.early_access.metamodel import ir, types, visitor, compiler
from relationalai.early_access.metamodel.typer.type_env import TypeEnv, TypeVar

DEFAULT_VERBOSITY = int(os.getenv('PYREL_TYPER_VERBOSITY', '0'))
DEFAULT_REPORT_ERRORS = False if os.getenv('PYREL_TYPER_REPORT_ERRORS', '0') == '0' else True

# Type System
# -----------
#
# Scalar types are either value types or entity types, not both.
# Value types (transitively) extend the built-in scalar types for which
# `is_value_base_type` holds.
# All other scalar types are entity types.
#
# Subtyping of scalar is declared explicitly in the model, currently as the
# `super_types` field in `ScalarType`, but this may change.
#
# The type system supports unions and tuples of types.
# Tuple types are covariant in their element types.
# Union types support the usual subtyping relation (for instance, a member of a
# union is a subtype of the union).
# We could, but currently do not, introduce common supertypes for unions.
#
# The `Any` type is used as a placeholder to mean "infer this type". `Any` is a
# scalar type.
# In particular, `Any` is not implicitly a supertype of any other type.
#
# List types are not allowed in the model and should have been rewritten to
# tuple types by the `RewriteListTypes` pass.
#
# Set types in the model indicate the multiplicity of the given field. They are
# not strictly types.
# For inference purposes, the element type is used as the type of the field,
# however when substituting inference results back into the model, the inferred
# type is wrapped in a `SetType`.
# Set types must be sets of scalar type (including `Any`).
#
# Type inference works as follows:
# - For each application of a relation:
#   - for input fields, bound the argument type by the field type (that is, arg
#     <: field; this is the standard rule for argument passing, types flow from
#     the argument to the field)
#   - for non-input fields (which could be input or output), equate the argument
#     type with the corresponding field type in the relation (= is more
#     efficient than adding two bounds: arg <: field and field <: arg)
# - For each variable, bound its type with its declared type.
# - For each field, bound its type with its declared type.
# - For default values, bound the variable type with the type of the default value.
# - These constraints build a graph of equivalence classes of nodes (fields and
# - vars). An edge a->b indicates that a is a subtype of b.
#   Each nodes has an associated set of upper and lower bounding scalar types.
# - Propagate upper bounds through the graph from supertype to subtype.
# - Propagate lower bounds through the graph from suptype to supertype.
# - Collapse cycles (SCCs) in the graph into an equivalence class.
# - For each equivalence class, union the upper bounds of all types in the
#   class. This is the inferred upper bound. Check that the inferred upper bound
#   of a node is a supertype of the all lower bounds of the node.
# - TODO: Update to match the new overloading strategy
#   If the type of a field cannot be inferred to any type (as happens when the
#   field is not used in any application), equate the relation with other
#   relations of the same name and arity, if any. Then recompute the bound
#   again. This has the effect of treating relations of the same name and arity
#   as overloads of each other, but only when necessary.
# - Replace the types in the model with the intersection of the inferred upper
#   bound and the declared type. This strictly lowers types to be more precise.


# TODO: Add inference for value types for the builtins according to the "lattice algorithm".
# https://docs.google.com/document/d/1G62zNQhUxgi_vlLEUgB3uKBKTsoIG770Xx2jtGAshIk/edit?tab=t.0#heading=h.u82mjk2nuyvr
# That is, if we find a builtin relation (just arithmetic? and aggregates?) that uses some value type,
# add constraints to ensure the result of the operation is also a value type.
# Currently, this is broken because overloads are only defined for the value base types (Int, Float, etc.)
# We thus only infer these base types for the result of the operation.

# TODO: special case for constants when used with value types.
# Cost + 1 should be a Cost, not an Int.

# TODO: conditional constraints
# These should simplify the value type problem:
# Consider PosInt <: Int.
# Add constraints for each builtin (WLOG, +):
#   a + b = c
#   if a <: PosInt and b <: PosInt then c <: PosInt
# This should also simplify overloading, since we can just add conditional constraints for each overload.
#   if x' <: Int then x' <: x1 and y' <: y1  (where x1 and y1 are field type variables of the overload for Int)
#
# The environment needs to keep track of the conditional constraints.
# When ever we update a type variable bound, we check the conditional constraints.
#

class BuildSubst(visitor.DAGVisitor):
    """
    A visitor that computes the types of the nodes in the model.
    """
    env: TypeEnv
    strict: bool
    subst: Dict[TypeVar, OrderedSet[ir.Type]]

    def __init__(self, env: TypeEnv, strict: bool):
        super().__init__()
        self.env = env
        self.strict = strict
        self.subst = {}

    def compute_type(self, x: TypeVar, declared_type: ir.Type, node: PyUnion[ir.Var, ir.Field], parent: Optional[ir.Node]) -> ir.Type:
        t = self.env.compute_type(x, node, x.index, parent)
        name = TypeVar.pretty_name(node, x.index, parent)
        lower_name = TypeVar.pretty_name(node, x.index, parent, lowercase=True)
        if t is not None and not types.is_null(t):
            if isinstance(t, ir.UnionType):
                ts = []
                for t2 in t.types:
                    t3 = BuildSubst._wrap_type(declared_type, t2)
                    if types.is_subtype(t3, declared_type):
                        ts.append(t3)
                if len(ts) == 1:
                    new_type = ts[0]
                elif ts:
                    new_type = types.union(*ts)
                else:
                    new_type = BuildSubst._wrap_type(declared_type, t)
            elif not isinstance(t, ir.ScalarType):
                # TODO: what should be done here? what are the cases?
                self.env._complain(node, f"{name} is inferred to be a non-scalar type {t}. Variables must have scalar type.")
                new_type = BuildSubst._wrap_type(declared_type, t)
            else:
                new_type = BuildSubst._wrap_type(declared_type, t)
            if not types.is_subtype(new_type, declared_type):
                self.env._complain(node, f"{name} inferred to be type {ir.type_to_string(new_type)} which is not a subtype of the declared type {ir.type_to_string(declared_type)}.")
            return new_type
        else:
            if self.strict:
                self.env._complain(node, f"Could not infer a type for {lower_name}")
            return declared_type

    def visit_var(self, node: ir.Var, parent: Optional[ir.Node]=None) -> None:
        # TODO: what if the parent is none what should be done here?
        x = self.env.get_type_var(node)
        t = self.compute_type(x, node.type, node, parent)
        x = x.find()
        if x not in self.subst:
            self.subst[x] = ordered_set(t)
        else:
            self.subst[x].add(t)

    def visit_field(self, node: ir.Field, parent: Optional[ir.Node]=None) -> None:
        # Substitute the intersection of the inferred type with the declared type.
        if isinstance(node.type, ir.TupleType):
            new_types = []
            for i in range(len(node.type.types)):
                x = self.env.get_type_var(node, i)
                t = self.compute_type(x, node.type.types[i], node, parent)
                x = x.find()
                if x not in self.subst:
                    self.subst[x] = ordered_set(t)
                else:
                    self.subst[x].add(t)
                new_types.append(t)
            new_type = ir.TupleType(tuple(new_types))
        else:
            x = self.env.get_type_var(node)
            t = self.compute_type(x, node.type, node, parent)
            new_type = t
            x = x.find()
            if x not in self.subst:
                self.subst[x] = ordered_set(new_type)
            else:
                self.subst[x].add(new_type)

    # Intersect the declared type with the inferred type, special casing set types.
    @staticmethod
    def _wrap_type(declared: ir.Type, inferred: ir.Type) -> ir.Type:
        return inferred

@dataclass
class CollectTypeConstraints(visitor.DAGVisitor):
    """
    A visitor that collects type constraints on a model.
    """
    def __init__(self, env: TypeEnv):
        super().__init__()
        self.env = env

    def visit_scalartype(self, node: ir.ScalarType, parent: Optional[ir.Node]=None):
        # Do not recurse.
        pass

    def visit_listtype(self, node: ir.ListType, parent: Optional[ir.Node]=None):
        # Do not recurse.
        pass

    def visit_uniontype(self, node: ir.UnionType, parent: Optional[ir.Node]=None):
        # Do not recurse.
        pass

    def visit_field(self, node: ir.Field, parent: Optional[ir.Node]=None):
        # Do not constrain field types to be <: Any.
        if isinstance(node.type, ir.TupleType):
            for i in range(len(node.type.types)):
                x = self.env.get_type_var(node, i)
                if not types.is_any(node.type.types[i]):
                    self.env.add_bound(x, node.type.types[i])
        elif isinstance(node.type, ir.UnionType):
            for t in node.type.types:
                if not types.is_any(t):
                    self.env.add_bound(node, t)
        elif isinstance(node.type, ir.ScalarType):
            if not types.is_any(node.type):
                self.env.add_bound(node, node.type)
        # Do not recurse. No need to visit the type.
        pass

    def visit_var(self, node: ir.Var, parent: Optional[ir.Node]=None):
        # Do not constrain field types to be <: Any.
        if isinstance(node.type, ir.UnionType):
            for t in node.type.types:
                if not types.is_any(t):
                    self.env.add_bound(node, t)
        elif isinstance(node.type, ir.ScalarType):
            if not types.is_any(node.type):
                self.env.add_bound(node, node.type)
            if not types.is_abstract_type(node.type):
                self.env.add_equality(node, node.type)

        # Do not recurse. No need to visit the type.
        pass

    def visit_default(self, node: ir.Default, parent: Optional[ir.Node]=None):
        # The variable's type should be a supertype of the default value.
        self.env.add_bound(node.value, node.var)
        # Recurse to add the constraints on the variable.
        return super().visit_default(node, parent)

    def visit_literal(self, node: ir.Literal, parent: Optional[ir.Node]=None):
        # Do not recurse. No need to visit the type.
        pass

    def visit_loop(self, node: ir.Loop, parent: Optional[ir.Node]=None):
        # The iterator should be a number.
        self.env.add_bound(node.iter, types.Number)
        return super().visit_loop(node, parent)

    def visit_update(self, node: ir.Update, parent: Optional[ir.Node]=None):
        if len(node.args) == len(node.relation.fields):
            # We have update R(x,y,z) where R is declared (t,u,v)
            # Bound each arg by the declared type of the field.
            for f, arg in zip(node.relation.fields, node.args):
                if isinstance(f.type, ir.TupleType) and isinstance(arg, Tuple):
                    # TODO: add this to Checker
                    assert len(arg) != len(f.type.types)
                    for i in range(len(f.type.types)):
                        f_global = self.env.get_type_var(f, index=i)
                        if f.input:
                            # Flow from argument to input field.
                            self.env.add_bound(arg[i], f_global)
                        else:
                            # Flow from argument to field, and back.
                            self.env.add_equality(arg[i], f_global)
                else:
                    f_global = self.env.get_type_var(f)
                    if f.input:
                        # Flow from argument to input field.
                        self.env.add_bound(arg, f_global)
                    else:
                        # Flow from argument to field, and back.
                        self.env.add_bound(arg, f_global)

        return super().visit_update(node, parent)

    def visit_annotation(self, node: ir.Annotation, parent: Optional[ir.Node]=None):
        # Do not recurse. No need to visit the relation again.
        pass

    def visit_lookup(self, node: ir.Lookup, parent: Optional[ir.Node]=None):
        # The constraints here are in two parts:
        # 1. The relation used in this particular application must be a subtype
        #    of the global relation. This is handled by using separate type
        #    variables for the fields of the relation, one for the global
        #    relation (with no context) and one for the instantiation of the
        #    relation here (with the Lookup as context).
        #    If the relation is not overloaded, we can just equate the instantiation
        #    with the global relation.
        # 2. The arguments to the lookup must have the same types as the
        #    instantiation of the relation here.

        # 1. The instantiated fields are a subtype of the global fields.
        for f in node.relation.fields:
            if isinstance(f.type, ir.TupleType):
                for i in range(len(f.type.types)):
                    f_instantiated = self.env.get_type_var(f, index=i, context=node)
                    f_global = self.env.get_type_var(f, index=i, context=None)
                    if node.relation.overloads:
                        self.env.add_bound(f_instantiated, f_global)
                    else:
                        self.env.add_equality(f_instantiated, f_global)
            else:
                f_instantiated = self.env.get_type_var(f, context=node)
                f_global = self.env.get_type_var(f)
                if node.relation.overloads:
                    self.env.add_bound(f_instantiated, f_global)
                else:
                    self.env.add_equality(f_instantiated, f_global)

        # 2. The argument types are equal to the instantiated fields.
        if len(node.args) == len(node.relation.fields):
            for f, arg in zip(node.relation.fields, node.args):
                if isinstance(f.type, ir.TupleType) and isinstance(arg, Tuple):
                    if len(arg) == len(f.type.types):
                        for i in range(len(f.type.types)):
                            f_instantiated = self.env.get_type_var(f, index=i, context=node)
                            if f.input:
                                self.env.add_bound(arg[i], f_instantiated)
                            else:
                                self.env.add_equality(arg[i], f_instantiated)
                    else:
                        self.env._complain(node, f"The arity of the lookup is not equal to the arity of the relation: {len(arg)} != {len(f.type.types)}")
                else:
                    f_instantiated = self.env.get_type_var(f, context=node)
                    if f.input:
                        self.env.add_bound(arg, f_instantiated)
                    else:
                        self.env.add_equality(arg, f_instantiated)

            # Also, equality should bind both arguments to each other
            if node.relation.name == "=":
                self.env.add_equality(node.args[0], node.args[1])

        return super().visit_lookup(node, parent)

    def visit_aggregate(self, node: ir.Aggregate, parent: Optional[ir.Node]=None):
        # This is the same as the Lookup case above, but the structure of the aggregation
        # makes it a bit more complex.

        agg = node.aggregation

        if len(agg.fields) < 1:
            return

        inputs = []
        outputs = []
        for f in agg.fields:
            if f.input:
                inputs.append(f)
            else:
                outputs.append(f)

        # 1. The instantiated fields are a subtype of the global fields.
        for f in agg.fields:
            if isinstance(f.type, ir.TupleType):
                for i in range(len(f.type.types)):
                    f_instantiated = self.env.get_type_var(f, index=i, context=node)
                    f_global = self.env.get_type_var(f, index=i, context=None)
                    if agg.overloads:
                        self.env.add_bound(f_instantiated, f_global)
                    else:
                        self.env.add_equality(f_instantiated, f_global)
            else:
                f_instantiated = self.env.get_type_var(f, context=node)
                f_global = self.env.get_type_var(f)
                if agg.overloads:
                    self.env.add_bound(f_instantiated, f_global)
                else:
                    self.env.add_equality(f_instantiated, f_global)

        # Now let's wire up the types of the arguments with the instantiated fields.

        # Inputs and outputs.
        if len(node.args) == len(inputs) + len(outputs):
            for arg, f in zip(node.args, inputs + outputs):
                if isinstance(f.type, ir.TupleType) and isinstance(arg, Tuple):
                    # TODO: add this to Checker
                    assert len(arg) != len(f.type.types)
                    for i in range(len(f.type.types)):
                        f_instantiated = self.env.get_type_var(f, index=i, context=node)
                        if f.input:
                            self.env.add_bound(arg[i], f_instantiated)
                        else:
                            self.env.add_equality(arg[i], f_instantiated)
                else:
                    f_instantiated = self.env.get_type_var(f, context=node)
                    if f.input:
                        self.env.add_bound(arg, f_instantiated)
                    else:
                        self.env.add_equality(arg, f_instantiated)

        return super().visit_aggregate(node, parent)

    def visit_rank(self, node: ir.Rank, parent: Optional[ir.Node]=None):
        self.env.add_equality(node.result, types.Int)
        return super().visit_rank(node, parent)

@dataclass
class ReconcileOverloads(visitor.DeprecatedPass):
    """
    Rewrite instantiated relations to their non-instantiated counterparts.
    This relies on UnifyInstantiatedRelations to find the non-instantiated relation.
    """
    env: TypeEnv = field(init=True)
    model: ir.Model = field(init=True)

    def find_matching_relation(self, abstract_relation: ir.Relation) -> Optional[ir.Relation]:
        """
        Find a non-instantiated relation with the same name and type signature.
        """
        # Find all non-instantiated relations in the model with the same name and arity that have
        # been unified with the given relation.
        # Unification was done by the UnifyInstantiatedRelations pass.
        candidates = []
        for r in abstract_relation.overloads:
            # If all the type variables match, consider it.
            if all(self.env.get_type_var(f1).find() == self.env.get_type_var(f2).find() for f1, f2 in zip(r.fields, abstract_relation.fields)):
                candidates.append(r)

        if len(candidates) == 0:
            self.env._complain(abstract_relation, f"Relation `{abstract_relation.name}` (id={abstract_relation.id}) has no matching overload.")
            return None
        elif len(candidates) == 1:
            return candidates[0]
        else:
            # If there's more than one matching candidate, union the fields types together.
            # TODO: or just filter out the candidates?
            # return abstract_relation.reconstruct(overloads=ordered_set(*candidates).frozen())
            new_fields = []
            for j, fields in enumerate(zip(*(r.fields for r in candidates))):
                ftypes = []
                name = abstract_relation.fields[j].name
                orig_type = abstract_relation.fields[j].type
                input = abstract_relation.fields[j].input
                for f in fields:
                    t = f.type
                    if isinstance(t, ir.ScalarType):
                        tv = self.env.get_type_var(f).find()
                        ftype = tv.compute_type()
                        ftype = types.intersect(ftype, t)
                        ftypes.append(ftype)
                    elif isinstance(t, ir.UnionType):
                        tv = self.env.get_type_var(f).find()
                        ftype = tv.compute_type()
                        for t2 in t.types:
                            ftype = types.intersect(ftype, t2)
                            ftypes.append(ftype)
                    elif isinstance(t, ir.TupleType):
                        # TODO: handle unions of tuples
                        for i, t2 in enumerate(t.types):
                            tv = self.env.find_type_var(f, i)
                            ftype = tv.compute_type()
                            ftype = types.intersect(ftype, t2)
                            ftypes.append(ftype)
                    else:
                        raise ValueError(f"Unexpected field type: {t}")
                new_type = types.union(orig_type, types.union(*ftypes))
                new_fields.append(ir.Field(name, new_type, input))

            new_relation = ir.Relation(
                name=abstract_relation.name,
                fields=tuple(new_fields),
                requires=abstract_relation.requires,
                annotations=abstract_relation.annotations,
                overloads=ordered_set().frozen(),
            )
            return new_relation

    def handle_lookup(self, node: ir.Lookup, parent: ir.Node):
        if node.relation.overloads:
            matching_relation = self.find_matching_relation(node.relation)
            if matching_relation is not None:
                return node.reconstruct(relation=matching_relation)
        return node

    def handle_aggregate(self, node: ir.Aggregate, parent: ir.Node):
        if node.aggregation.overloads:
            matching_relation = self.find_matching_relation(node.aggregation)
            if matching_relation is not None:
                return node.reconstruct(aggregation=matching_relation)
        return node


@dataclass
class SubstituteTypes(visitor.DeprecatedPass):
    """
    A visitor that substitutes types back into the model.
    """
    env: TypeEnv = field(init=True)
    subst: Dict[TypeVar, ir.Type] = field(init=True)

    def handle_var(self, node: ir.Var, parent: ir.Node) -> ir.Var:
        x = self.env.find_type_var(node)
        new_type = self.subst[x]
        disjuncts = []
        if isinstance(new_type, ir.UnionType):
            disjuncts = new_type.types
        else:
            disjuncts = [new_type]
        for t in disjuncts:
            if not isinstance(t, ir.ScalarType):
                self.env._complain(node, f"Variable {node.name} inferred to be a non-scalar type {ir.type_to_string(t)}. Variables must have scalar type.")
        return node.reconstruct(type=new_type)

    def handle_field(self, node: ir.Field, parent: ir.Node) -> ir.Field:
        # Substitute the intersection of the inferred type with the declared type.
        if isinstance(node.type, ir.TupleType):
            new_types = []
            for i in range(len(node.type.types)):
                x = self.env.find_type_var(node, i)
                t = self.subst[x]
                new_types.append(t)
            new_type = ir.TupleType(tuple(new_types))
        else:
            x = self.env.find_type_var(node)
            new_type = self.subst[x]
        return node.reconstruct(type=new_type)

@dataclass
class Typer(compiler.Pass):
    """
    A pass that performs type inference on a model.
    The pass also checks that the model is well-formed.
    Diagnostics are reported for ill-formed or ill-typed models.

    The main idea is to traverse the model and collect type constraints.
    These are then solved and substituted back into the model.
    """

    # Should we perform stricter checks on the inferred types?
    strict: bool = field(default=False, init=False)

    # How verbose to be with debug output, 0 is off.
    verbosity: int = field(default=DEFAULT_VERBOSITY, init=False)

    # Temporarily in in case there are bugs. Set this to default to False
    # if type inference is causing too many issues.
    report_errors: bool = field(default=DEFAULT_REPORT_ERRORS, init=False)

    def rewrite(self, model: ir.Model, cache) -> ir.Model:
        if self.verbosity:
            print("\n")
            print("\nInitial model:")
            if self.verbosity > 1:
                ir.dump(model)
            else:
                print(model)

        # Type inference.
        env = TypeEnv(model, self.strict, self.verbosity)
        collector = CollectTypeConstraints(env)
        model.accept(collector)

        env.solve()

        # Substitute the types back into the model.
        build_subst = BuildSubst(env, self.strict)
        model.accept(build_subst)

        # Check that the substitutions are consistent.
        # Otherwise, we can get into a situation where we infer {S;T} and
        # substitute T in one place, but S in another.
        subst: Dict[TypeVar, ir.Type] = {}
        for x, ts in build_subst.subst.items():
            assert x == x.find()
            t = ts.list[0]
            for u in ts.list[1:]:
                if not types.is_subtype(t, u):
                    t = u
                elif not types.is_subtype(u, t):
                    env._complain(x.node, f"Type variable {x} is inferred to be {ir.type_to_string(t)} but it is used as the non-matching type {ir.type_to_string(u)}.")
            subst[x] = t

        do_subst = SubstituteTypes(env, subst)
        model2 = do_subst.walk(model)

        # Assert that there are no type errors
        if env.diags:
            error_count = len(env.diags)
            error_header = "TYPE ERROR\n" if error_count == 1 else f"{error_count} TYPE ERRORS\n"
            formatted_errors = [error_header] + [f"* (Node id={env.diags[i].node.id}) {env.diags[i].msg}" for i in range(error_count)]
            if self.report_errors:
                raise Exception("\n".join(formatted_errors))
            else:
                print("\n".join(formatted_errors))

        if self.verbosity:
            print("After substitution:")
            if self.verbosity > 1:
                ir.dump(model2)
            else:
                print(model2)

        reconcile = ReconcileOverloads(env, model2)
        model3 = reconcile.walk(model2)

        if self.verbosity:
            print("After reconcilation:")
            if self.verbosity > 1:
                ir.dump(model3)
            else:
                print(model3)

        return model3
