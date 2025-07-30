"""
Helpers to analyze the metamodel IR in ways that are specific to Rel generation.
"""
from __future__ import annotations

from typing import cast, Optional
from relationalai.early_access.metamodel import ir, helpers, factory as f
from relationalai.early_access.metamodel.util import OrderedSet
from relationalai.early_access.rel.dependency import AnalysisContext


def outer_join_prefix(nullable_logicals: OrderedSet[ir.Logical], groups: dict[str, OrderedSet[ir.Task]]) -> list[ir.Var]:
    """ Check if it is possible to use an outer join on the logical that has these nullable
    logicals and these groups of tasks. This function returns a list of prefix variables
    for the outer join.

    There are several requirements to use the outer join. If some is not met, the
    function returns an empty list
    """
    # all nested logicals must be nullable
    if len(nullable_logicals) != len(groups["logicals"]):
        return []

    # at this point, all nested logicals are nullable, but they should only have a single hoisted variable
    for logical in nullable_logicals:
        if len(logical.hoisted) != 1:
            return []

    # outer joins only work on outputs
    if "output" not in groups or len(groups["output"]) != 1:
        return []
    output = cast(ir.Output, groups["output"].some())

    # the output variables must be a prefix + nullable variables; the length of the
    # prefix is the number of extra aliases in the output
    prefix_length = len(output.aliases) - len(nullable_logicals)
    if prefix_length < 1:
        return []

    # get the hoisted vars from the nullable logicals, a bit messy
    logical_hoisted_vars = OrderedSet.from_iterable([cast(ir.Default, logical.hoisted[0]).var for logical in nullable_logicals])
    prefix=[]
    i = 0
    for _, var in output.aliases:
        if i < prefix_length:
            # the first prefix_length aliases are the prefix variables
            prefix.append(var)
            i += 1
        else:
            # the remaining output variables should be exposed one by one by the logicals
            if var not in logical_hoisted_vars:
                return []
            logical_hoisted_vars.remove(var)
    # basically an assertion as this should be empty if we got here
    if logical_hoisted_vars:
        return []

    # all nullable logicals must join with all the prefix variables
    for logical in nullable_logicals:
        vars = helpers.collect_implicit_vars(logical)
        for prefix_var in prefix:
            if prefix_var not in vars:
                return []

    return prefix


def extract(task: ir.Task, body: OrderedSet[ir.Task], exposed_vars: list[ir.Var], ctx: AnalysisContext, prefix: Optional[str]=None) -> ir.Relation:
    """
    Extract into this Analysiscontext a new top level Logical that contains this body plus a
    derive task into a new temporary relation, which is also registered with the ctx.
    The exposed_vars determine the arguments of this temporary relation. The prefix
    can be used to customize the name of the relation, which defaults to the task kind.

    Return the temporary relation created for the extraction.
    """

    # TODO: review variable rewrites, i.e. when we extract a new logical, we should remap variables
    p = prefix if prefix else task.kind

    # new relation to derive the aggregation into
    connection = f.relation(f"_{p}_{task.id}", [f.field(v.name, v.type) for v in exposed_vars])
    ctx.relations.append(connection)

    # add derivation to the extracted body
    body.add(f.derive(connection, exposed_vars))

    # extract the body
    ctx.top_level.append(ir.Logical(task.engine, tuple(), tuple(body)))

    # return a reference to the connection relation
    return connection
