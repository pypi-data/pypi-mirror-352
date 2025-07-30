from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Tuple, cast

from relationalai.early_access.metamodel import ir, compiler as c, visitor as v, factory as f, builtins, types, \
    rewrite as rw, helpers
from relationalai.early_access.metamodel.typer import typer2, checker
from relationalai.early_access.metamodel.builtins import from_cdc_annotation, concept_relation_annotation
from relationalai.early_access.metamodel.types import Hash, String, Number, Int, Decimal, Bool, Date, DateTime, Float
from relationalai.early_access.metamodel.util import FrozenOrderedSet, OrderedSet, frozen, ordered_set, filter_by_type, \
    NameCache
from relationalai.early_access.devmode import sql, rewrite


class Compiler(c.Compiler):
    def __init__(self, skip_denormalization:bool=False):
        rewrites = [
            checker.Checker(),
            typer2.InferTypes(),
            rw.GarbageCollectNodes(),
        ]
        if not skip_denormalization:
            # group updates, compute SCCs, use Sequence to denote their order
            rewrites.append(rewrite.Denormalize())
        super().__init__(rewrites)
        self.model_to_sql = ModelToSQL()

    def do_compile(self, model: ir.Model, options:dict={}) -> str:
        return str(self.model_to_sql.to_sql(model))


@dataclass
class ModelToSQL:
    """ Generates SQL from an IR Model, assuming the compiler rewrites were done. """

    relation_name_cache: NameCache = field(default_factory=NameCache)

    def to_sql(self, model: ir.Model) -> sql.Program:
        self._register_external_relations(model)
        return sql.Program(self._generate_statements(model))

    def _generate_statements(self, model: ir.Model) -> list[sql.Node]:
        statements: list[sql.Node] = []
        for relation in model.relations:
            if self._is_table_creation_required(relation):
                statements.append(self._create_table(cast(ir.Relation, relation)))
        root = cast(ir.Logical, model.root)
        for child in root.body:
            if isinstance(child, ir.Logical):
                statements.extend(self._create_statement(cast(ir.Logical, child)))
            elif isinstance(child, ir.Union):
                statements.append(self._create_recursive_view(cast(ir.Union, child)))
        return statements

    #--------------------------------------------------
    # SQL Generation
    #--------------------------------------------------
    def _create_table(self, r: ir.Relation) -> sql.Node:
        return sql.CreateTable(
            sql.Table(self._relation_name(r),
                list(map(lambda f: sql.Column(f.name, self._convert_type(f.type)), r.fields))
            ))

    def _create_recursive_view(self, union: ir.Union) -> sql.Node:
        assert len(union.tasks) == 2
        assert isinstance(union.tasks[0], ir.Logical)
        assert isinstance(union.tasks[1], ir.Logical)

        def make_case_select(logical: ir.Logical):
            # TODO - improve the typing info to avoid these casts
            lookups = cast(list[ir.Lookup], filter_by_type(logical.body, ir.Lookup))
            # TODO - assuming a single update per case
            update = v.collect_by_type(ir.Update, logical).some()

            # TODO - rewriting references to the view, to use the CTE instead, with _rec
            new_lookups = []
            for lookup in lookups:
                if lookup.relation == update.relation:
                    new_lookups.append(f.lookup(
                        ir.Relation(f"{self._relation_name(lookup.relation)}_rec", lookup.relation.fields,
                                    frozen(), frozen()), lookup.args, lookup.engine))
                else:
                    new_lookups.append(lookup)

            aliases = []
            for i, arg in enumerate(update.args):
                aliases.append((update.relation.fields[i].name, arg))
            return self._make_select(new_lookups, aliases)

        # get a representative update
        update = v.collect_by_type(ir.Update, union).some()

        # TODO - maybe this should be more like INSERT INTO a table than a view?
        return sql.CreateView(self._relation_name(update.relation),
            sql.CTE(True, f"{self._relation_name(update.relation)}_rec", [f.name for f in update.relation.fields], [
                make_case_select(cast(ir.Logical, union.tasks[0])),
                make_case_select(cast(ir.Logical, union.tasks[1]))
            ]))

    def _create_statement(self, task: ir.Logical):

        # TODO - improve the typing info to avoid these casts
        lookups = cast(list[ir.Lookup], filter_by_type(task.body, ir.Lookup))
        updates = cast(list[ir.Update], filter_by_type(task.body, ir.Update))
        outputs = cast(list[ir.Output], filter_by_type(task.body, ir.Output))
        logicals = cast(list[ir.Logical], filter_by_type(task.body, ir.Logical))
        constructs = cast(list[ir.Construct], filter_by_type(task.body, ir.Construct))
        var_to_rank = {
            r.result: r
            for logical in logicals
            for r in logical.body
            if isinstance(r, ir.Rank)
        } if logicals else {}

        statements = []
        # TODO - this is simplifying soooo much :crying_blood:
        if updates and not lookups:
            # TODO: this is assuming that the updates are all static values
            # insert static values: INSERT INTO ... VALUES ...
            for u in updates:
                r = u.relation
                tuples = self._get_tuples(task, u)
                for tuple in tuples:
                    statements.append(
                        sql.Insert(self._relation_name(r), [f.name for f in r.fields], tuple, None)
                    )
        elif updates and lookups:
            id_var_to_construct = {c.id_var: c for c in constructs} if constructs else {}
            # insert values that match a query: INSERT INTO ... SELECT ... FROM ... WHERE ...
            for u in updates:
                r = u.relation
                aliases = []
                # We shouldn’t create or populate tables for value types that can be directly sourced from existing Snowflake tables.
                if not self._is_value_type_population_relation(r):
                    for i, arg in enumerate(u.args):
                        field_name = r.fields[i].name
                        if isinstance(arg, ir.Var):
                            var_task = id_var_to_construct.get(arg) or var_to_rank.get(arg)
                            if task:
                                aliases.append((field_name, arg, var_task))
                            else:
                                aliases.append((field_name, arg))
                        else:
                            aliases.append((field_name, arg))

                    statements.append(
                        sql.Insert(self._relation_name(r),
                                   [f.name for f in r.fields], [],
                                   self._make_select(lookups, aliases, True)
                        )
                    )
        elif outputs and (lookups or logicals):
            # output a query: SELECT ... FROM ... WHERE ...
            aliases = []
            for output in outputs:
                for key, arg in output.aliases:
                    if isinstance(arg, ir.Var) and arg in var_to_rank:
                        aliases.append((key, arg, var_to_rank[arg]))
                    else:
                        aliases.append((key, arg))
            # TODO: some of the lookup relations we wrap into logical and we need to get them from it.
            #  Check if this is the right thing to do.
            if logicals:
                for logical in logicals:
                    inner_lookups = cast(list[ir.Lookup], filter_by_type(logical.body, ir.Lookup))
                    lookups.extend(inner_lookups)
            statements.append(self._make_select(lookups, aliases))
            pass
        elif logicals:
            for logical in logicals:
                statements.extend(self._create_statement(logical))
        else:
            raise Exception(f"Cannot create SQL statement for:\n{task}")
        return statements

    def _make_select(self, lookups: list[ir.Lookup], outputs: list[Tuple[str, ir.Value]|Tuple[str, ir.Value, ir.Task]],
                     distinct: bool = False) -> sql.Select:
        table_lookups = filter(lambda t: not builtins.is_builtin(t.relation), lookups)
        froms = []
        sql_vars: dict[ir.Lookup, str] = dict() # one var per table lookup
        var_column: dict[Tuple[ir.Var, ir.Lookup], ir.Field] = dict()
        var_sql_var: dict[ir.Var, str] = dict()
        var_lookups: dict[ir.Var, OrderedSet[ir.Lookup]] = dict()
        i = 0
        for lookup in table_lookups:
            varname = f"v{i}"
            i += 1
            froms.append(sql.From(self._relation_name(lookup.relation), varname))
            sql_vars[lookup] = varname
            j = 0
            for arg in lookup.args:
                if isinstance(arg, ir.Var):
                    var_column[arg, lookup] = lookup.relation.fields[j]
                    var_sql_var[arg] = varname
                    if arg not in var_lookups:
                        var_lookups[arg] = ordered_set()
                    var_lookups[arg].add(lookup)
                j += 1

        disjoined_builtins: dict[ir.Var, set[str]] = defaultdict(set)
        computed_outputs: dict[ir.Var, str] = dict()
        output_vars = {
            output[1]
            for output in outputs
            if isinstance(output[1], ir.Var)
        }
        # example: c = a - b in the IR it is (a - b = d) and (d = c) and we add `d` to the `intermediate_builtin_vars`
        builtin_lookups = [t for t in lookups if builtins.is_builtin(t.relation)]
        intermediate_builtin_vars: set[ir.Var] = {
            arg for lookup in builtin_lookups
            for arg in lookup.args
            if isinstance(arg, ir.Var) and arg not in var_lookups
        }

        wheres: list[sql.Expr] = []
        # uses of built-in expressions
        def reference(v):
            if isinstance(v, ir.Var):
                # TODO - assuming the built-in reference was grounded elsewhere
                lookup = var_lookups[v].some()
                return f"{var_sql_var[v]}.{var_column[(v, lookup)].name}"
            return str(v)  # assuming a literal
        for lookup in builtin_lookups:
            args = lookup.args
            lhs_raw, rhs_raw = args[0], args[1]

            # TODO - assuming infix binary or ternary operators here
            lhs = lhs_raw if lhs_raw in intermediate_builtin_vars else reference(lhs_raw)
            rhs = rhs_raw if rhs_raw in intermediate_builtin_vars else reference(rhs_raw)

            if len(args) == 3 and isinstance(args[2], ir.Var):
                out_var = args[2]
                expr = f"{lhs} {self._relation_name(lookup.relation)} {rhs}"

                if out_var in output_vars:
                    computed_outputs[out_var] = expr
                else:
                    # case when this is an intermediate result
                    # example: c = a - b in the IR it is (a - b = d) and (d = c)
                    disjoined_builtins[out_var].add(expr)
            else:
                # Replace intermediate vars with disjoined expressions
                if isinstance(lhs, ir.Var):
                    lhs = disjoined_builtins[lhs].pop()
                if isinstance(rhs, ir.Var):
                    rhs = disjoined_builtins[rhs].pop()
                wheres.append(sql.Terminal(f"{lhs} {self._relation_name(lookup.relation)} {rhs}"))
        # if there are 2 lookups for the same variable, we need a join
        for arg, lookup_set in var_lookups.items():
            if len(lookup_set) > 1:
                refs = [f"{sql_vars[lu]}.{var_column[cast(ir.Var, arg), lu].name}" for lu in lookup_set]
                # join variable references pairwise (e.g. "x.id = y.id AND y.id = z.id")
                for lhs, rhs in zip(refs, refs[1:]):
                    wheres.append(sql.Terminal(f"{lhs} = {rhs}"))

        # finally, compute what the select will return
        vars = []
        not_null_vars = ordered_set()
        for output in outputs:
            alias, var = output[0], output[1]
            task = output[2] if len(output) > 2 else None
            if isinstance(var, ir.Var):
                if var in var_lookups:
                    lookup = var_lookups[var].some()
                    vars.append(sql.VarRef(sql_vars[lookup], var_column[var, lookup].name, alias))
                    if from_cdc_annotation in lookup.relation.annotations:
                        not_null_vars.add(f"{sql_vars[lookup]}.{var_column[var, lookup].name}")
                elif var in computed_outputs:
                    # TODO - abusing VarRef.name here, it's actually an expression here. Fix it!
                    vars.append(sql.VarRef(computed_outputs[var], None, alias))
                elif task:
                    if isinstance(task, ir.Construct):
                        # Generate constructions like hash(`x`, `y`, TABLE_ALIAS.COLUMN_NAME) as `alias`
                        elements = []
                        for v in task.values:
                            if isinstance(v, ir.Var):
                                lookup = var_lookups[v].some()
                                lookup_var = f"{sql_vars[lookup]}.{var_column[v, lookup].name}"
                                elements.append(lookup_var)
                                if from_cdc_annotation in lookup.relation.annotations:
                                    not_null_vars.add(lookup_var)
                            else:
                                elements.append(self._convert_value(v, True))
                        vars.append(sql.VarRef(f"hash({', '.join(elements)})", None, alias))
                    elif isinstance(task, ir.Rank):
                        order_by_vars = []
                        for arg, is_ascending in zip(task.args, task.arg_is_ascending):
                            order_by_vars.append(sql.OrderByVar(reference(arg), is_ascending))
                        partition_by_vars = [reference(arg) for arg in task.group] if task.group else []
                        vars.append(sql.RowNumberVar(order_by_vars, partition_by_vars, alias))
            else:
                # TODO - abusing even more here, because var is a value!
                vars.append(sql.VarRef(str(var), None, alias))

        if not_null_vars:
            wheres.extend(sql.NotNull(var) for var in not_null_vars)

        # conjunction of wheres
        if len(wheres) == 0:
            where = None
        elif len(wheres) == 1:
            where = sql.Where(wheres[0])
        else:
            where = sql.Where(sql.And(wheres))

        return sql.Select(distinct, vars, froms, where)

    def _get_tuples(self, logical: ir.Logical, u: ir.Update):
        """
        Get a list of tuples to perform this update.

        This function traverses the update args, assuming they contain only static values or
        variables bound to a construct task, and generates a list of tuples to insert. There
        may be multiple tuples because arguments can be lists of values bound to a field
        whose role is multi.
        """
        # TODO - this only works if the variable is bound to a Construct task, we need a more general approach.
        values = []
        for a in u.args:
            if isinstance(a, ir.Var):
                for t in logical.body:
                    if isinstance(t, ir.Construct) and t.id_var == a:
                        values.append(f"hash({', '.join([self._convert_value(v, True) for v in t.values])})")
                        break
            elif isinstance(a, FrozenOrderedSet):
                values.append(frozen(*[self._convert_value(v) for v in a]))
            else:
                values.append(self._convert_value(a))
        return self._product(values)

    def _product(self, values):
        """ Compute a cartesian product of values when the value is a FrozenOrderedSet. """
        # TODO - some pass needs to check that this is correct, i.e. that we are using a
        # FrozenOrderedSet only if the field is of role multi.
        tuples = [[]]
        for value in values:
            if isinstance(value, FrozenOrderedSet):
                tuples = [prev + [element] for prev in tuples for element in value]
            else:
                tuples = [prev + [value] for prev in tuples]
        return tuples

    def _convert_value(self, v, quote_numbers:bool=False) -> str:
        """ Convert the literal value in v to a SQL value."""
        if isinstance(v, str):
            return f"'{v}'"
        if isinstance(v, ir.ScalarType):
            return f"'{v.name}'"
        if isinstance(v, ir.Literal):
            return self._convert_value(v.value, quote_numbers)
        return v if not quote_numbers else f"'{v}'"

    BUILTIN_CONVERSION = {
        Hash: "DECIMAL(38, 0)",
        String: "TEXT",
        Number: "DOUBLE",
        Int: "INT",
        Decimal: "DECIMAL(13, 2)",
        Bool: "BOOLEAN",
        Date: "DATE",
        DateTime: "DATETIME",
        Float: "FLOAT(53)",
    }
    def _convert_type(self, t: ir.Type) -> str:
        """ Convert the type t into the equivalent SQL type."""
        # entities become DECIMAL(38, 0)
        if not types.is_builtin(t) and not types.is_value_type(t):
            return "DECIMAL(38, 0)"

        # convert known builtins
        base_type = typer2.to_base_primitive(t)
        if isinstance(base_type, ir.ScalarType) and base_type in self.BUILTIN_CONVERSION:
            return self.BUILTIN_CONVERSION[base_type]
        raise Exception(f"Unknown built-in type: {t}")

    def _is_table_creation_required(self, r: ir.Relation) -> bool:
        """ Check if the relation should be created as a table in SQL. """
        # Skip built-in relations, builtin overloads and CDC relations
        if builtins.is_builtin(r) or r in builtins.builtin_overloads or from_cdc_annotation in r.annotations:
            return False
        # Skip value type population relations
        return not self._is_value_type_population_relation(r)

    @staticmethod
    def _is_value_type_population_relation(r: ir.Relation) -> bool:
        """ Check if the relation is a value type relation. """
        if not r.fields or len(r.fields) != 1:
            return False
        return types.is_value_type(r.fields[0].type) and concept_relation_annotation in r.annotations

    def _relation_name(self, relation: ir.Relation):
        if helpers.is_external(relation) or helpers.builtins.is_builtin(relation):
            return relation.name
        return self.relation_name_cache.get_name(relation.id, relation.name, helpers.relation_name_prefix(relation))

    def _register_external_relations(self, model: ir.Model):
        # force all external relations to get a name in the cache, so that internal relations
        # cannot use those names in _relation_name
        for r in model.relations:
            if helpers.is_external(r):
                self.relation_name_cache.get_name(r.id, r.name)
