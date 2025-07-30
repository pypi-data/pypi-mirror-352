"""
Helpers to analyze the metamodel IR.
"""
from __future__ import annotations

from typing import cast, Tuple, Iterable
from relationalai.early_access.metamodel import ir, util, visitor, builtins, types
from relationalai.early_access.metamodel.util import OrderedSet, FrozenOrderedSet


#--------------------------------------------------
# Checks
#--------------------------------------------------

def is_external(relation: ir.Relation):
   """ Whether this relation is external, by being marked with the external annotation. """
   return builtins.external_annotation in relation.annotations

def is_aggregate_input(var: ir.Var, agg: ir.Aggregate):
    """ Whether this var is an input to this aggregation. """
    return (var in agg.args and agg.aggregation.fields[agg.args.index(var)].input)

def is_effective_logical(n: ir.Task):
    """ Whether this task is a Logical and contains an Update child, recursively. """
    return isinstance(n, ir.Logical) and len(visitor.collect_by_type(ir.Update, n)) > 0

def is_nullable_logical(n: ir.Task):
    """ Whether this task is a Logical that contains a hoisted variable with a None default. """
    return isinstance(n, ir.Logical) and any(isinstance(v, ir.Default) and v.value is None for v in n.hoisted)

def relation_is_subtype(r1: ir.Relation, r2: ir.Relation):
    if r1 is r2:
        return True
    if len(r1.fields) != len(r2.fields):
        return False
    return all(types.is_subtype(f1.type, f2.type) for f1, f2 in zip(r1.fields, r2.fields))

def relation_is_proper_subtype(r1: ir.Relation, r2: ir.Relation):
    if r1 is r2:
        return False
    if relation_is_subtype(r1, r2):
        return any(types.is_proper_subtype(f1.type, f2.type) for f1, f2 in zip(r1.fields, r2.fields))
    else:
        return False

def relation_name_prefix(relation: ir.Relation):
    prefix = ""
    if len(relation.fields) > 0 and builtins.concept_relation_annotation not in relation.annotations:
        main_type = relation.fields[0].type
        if (isinstance(main_type, ir.ScalarType) and
            main_type not in types.builtin_types and
            not relation.name.startswith(main_type.name) and
            not relation.name.startswith("_")):
                prefix = f"{main_type.name.lower()}_"
    return prefix

#--------------------------------------------------
# Filters
#--------------------------------------------------

def aggregate_outputs(agg: ir.Aggregate) -> list[ir.Var]:
    """ Get the list of vars bound to the outputs of this aggregation. """
    return list(filter(lambda arg: isinstance(arg, ir.Var) and not is_aggregate_input(arg, agg), agg.args)) # type: ignore

def effective_logicals(tasks: OrderedSet[ir.Task]) -> OrderedSet[ir.Logical]:
    """ Filter tasks to return only the Logical tasks that are effective. """
    return util.OrderedSet.from_iterable(filter(lambda t: is_effective_logical(t), tasks))

def nullable_logicals(tasks: OrderedSet[ir.Task]) -> OrderedSet[ir.Logical]:
    """ Filter tasks to return only the Logical tasks that are nullable. """
    return util.OrderedSet.from_iterable(filter(lambda t: is_nullable_logical(t), tasks))

def hoisted_vars(hoisted: Iterable[ir.VarOrDefault]) -> list[ir.Var]:
    """ Extract the vars from defaults in the hoisted list, returning just Vars. """
    return [v.var if isinstance(v, ir.Default) else v for v in hoisted]

def vars(args: Tuple[ir.Value, ...]) -> list[ir.Var]:
    """ Filter this list of values, keeping only Vars. """
    return cast(list[ir.Var], list(filter(lambda v: isinstance(v, ir.Var), util.flatten_tuple(args, ir.Value))))

def output_vars(aliases: FrozenOrderedSet[Tuple[str, ir.Value]]) -> list[ir.Var]:
    return [alias[1] for alias in aliases if isinstance(alias[1], ir.Var)]

def output_values(aliases: FrozenOrderedSet[Tuple[str, ir.Value]]) -> list[ir.Value]:
    return [alias[1] for alias in aliases]

#--------------------------------------------------
# Visitors/Collectors
#--------------------------------------------------

def collect_vars(*nodes: ir.Node) -> OrderedSet[ir.Var]:
    """ Collect all Vars starting at this node. """
    return cast(OrderedSet[ir.Var],
        visitor.collect_by_type(ir.Var, *nodes)
    )

def collect_quantified_vars(*nodes: ir.Node) -> OrderedSet[ir.Var]:
    """ Collect all Vars that are children of Exists and ForAll. """
    return cast(OrderedSet[ir.Var],
        visitor.collect(
            lambda n, parent: isinstance(n, ir.Var) and isinstance(parent, (ir.Exists, ir.ForAll)),
            *nodes)
    )

def collect_aggregate_vars(*nodes: ir.Node) -> OrderedSet[ir.Var]:
    """ Collect vars that are declared by aggregates in Rel (projection + over). """
    return cast(OrderedSet[ir.Var],
        # TODO - when dealing with multiple aggregations we will need to consider groupbys
        visitor.collect(
            lambda n, parent:
                # parent of var is an aggregate and either
                isinstance(parent, ir.Aggregate) and isinstance(n, ir.Var) and (
                # var is in the projection
                n in parent.projection or
                # var is an input to the aggregation's relation
                is_aggregate_input(n, parent)
                ),
            *nodes)
    )

def collect_rank_vars(*nodes: ir.Node) -> OrderedSet[ir.Var]:
    """ Collect vars that are declared by ranks in Rel (projection + over). """
    return cast(OrderedSet[ir.Var],
        # TODO - when dealing with multiple aggregations we will need to consider groupbys
        visitor.collect(
            lambda n, parent:
                # parent of var is an aggregate and either
                isinstance(parent, ir.Rank) and isinstance(n, ir.Var) and (
                # var is in the projection
                n in parent.projection or
                n in parent.args
                ),
            *nodes)
    )

def collect_implicit_vars(*nodes: ir.Node) -> OrderedSet[ir.Var]:
    """ Collect vars except the quantified and aggregate vars. """
    if not nodes:
        return util.ordered_set()
    return collect_vars(*nodes) - collect_quantified_vars(*nodes) - collect_aggregate_vars(*nodes) - collect_rank_vars(*nodes)


#--------------------------------------------------
# Useful node categories
#--------------------------------------------------

BINDERS = (ir.Lookup, ir.Construct, ir.Aggregate, ir.Exists, ir.Data, ir.Not)
COMPOSITES = (ir.Logical, ir.Sequence, ir.Union, ir.Match, ir.Until, ir.Wait)
EFFECTS = (ir.Update, ir.Output)
