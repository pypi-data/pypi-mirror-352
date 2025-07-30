from __future__ import annotations
from dataclasses import dataclass
from typing import cast, Optional

from relationalai.early_access.metamodel import ir, factory as f, helpers, visitor
from relationalai.early_access.metamodel.compiler import Pass, group_tasks
from relationalai.early_access.metamodel.util import OrderedSet, ordered_set
from relationalai.early_access.rel import metamodel_utils
from relationalai.early_access.rel.dependency import AnalysisContext, ctx_frame

class Flatten(Pass):
    """
    Traverses the model's root to flatten it as much as possible. The result of this pass is
    a Logical root where all nested tasks that represent a rule in Rel are extraced to the
    top level.

    - nested logical with updates becomes a top-level logical (a rule)

    From:
        Logical
            Logical
                lookup1   <- scope is spread
                Logical
                    lookup2
                    derive foo
                Logical
                    lookup3
                    derive bar
    To:
        Logical
            Logical
                lookup1
                lookup2
                derive foo
            Logical
                lookup1
                lookup3
                derive bar

    - nested logical with aggregates becomes a top-level logical (a rule representing an aggregation)

    From:
        Logical
            Logical
                lookup1
                Logical
                    lookup2
                    aggregate1
                Logical
                    lookup3
                    aggregate2
                output
    To:
        Logical
            Logical
                lookup1
                lookup2
                aggregate1
                derive tmp1
            Logical
                lookup1
                lookup3
                aggregate2
                derive tmp2
            Logical
                lookup1
                lookup tmp1
                lookup tmp2
                output

    - a union becomes a top-level logical for each branch, writing into a temporary relation,
    and a lookup from that relation.

    From:
        Logical
            Logical
                Union
                    Logical
                        lookup1
                    Logical
                        lookup2
                output
    To:
        Logical
            Logical
                lookup1
                derive tmp1
            Logical
                lookup2
                derive tmp1
            Logical
                lookup tmp1
                output

    - a match becomes a top-level logical for each branch, each writing into its own temporary
    relation and a lookup from the last relation. The top-level logical for a branch derives
    into the temporary relation negating the previous branch:

    From:
        Logical
            Logical
                Match
                    Logical
                        lookup1
                    Logical
                        lookup2
                output
    To:
        Logical
            Logical
                lookup1
                derive tmp1
            Logical
                Union            <- tmp1() or (not temp1() and lookup2())
                    lookup tmp1
                    Logical
                        Not
                            lookup tmp1
                        lookup2
                        derive tmp2
            Logical
                lookup tmp2
                output
    """

    #--------------------------------------------------
    # Public API
    #--------------------------------------------------
    def rewrite(self, model: ir.Model, cache) -> ir.Model:
        # create the dependency analysis context
        ctx = AnalysisContext(model.root)

        # rewrite the root
        result = self.handle(model.root, ctx)

        # the new body contains the extracted top level logicals and maybe the rewritten root
        body = ctx.top_level if result.replacement is None else ctx.top_level + [result.replacement]

        # create the new model, updating relations and root
        return ir.Model(
            model.engines,
            OrderedSet.from_iterable(model.relations).update(ctx.relations).frozen(),
            model.types,
            ir.Logical(model.root.engine, tuple(), tuple(body))
        )

    #--------------------------------------------------
    # IR handlers
    #--------------------------------------------------

    @dataclass
    class HandleResult():
        replacement: Optional[ir.Task]
        updates: Optional[OrderedSet[ir.Update]] = None

    def handle(self, task: ir.Task, ctx: AnalysisContext) -> Flatten.HandleResult:
        if isinstance(task, ir.Logical):
            return self.handle_logical(task, ctx)
        elif isinstance(task, ir.Union):
            return self.handle_union(task, ctx)
        elif isinstance(task, ir.Match):
            return self.handle_match(task, ctx)
        elif isinstance(task, ir.Require):
            return self.handle_require(task, ctx)
        else:
            return Flatten.HandleResult(task)

    def handle_logical(self, task: ir.Logical, ctx: AnalysisContext):
        # create frame to process the children
        with ctx_frame(ctx, task) as frame:

            # keep track of what's the result of handling nested composites
            composites = group_tasks(task.body, {
                "composites": helpers.COMPOSITES
            })["composites"]
            all_composites_removed = len(composites) > 0

            # recursively handle children, collecting the replacements in the body
            body:OrderedSet[ir.Task] = ordered_set()
            for child in task.body:
                result = self.handle(child, ctx)
                if result.replacement is not None:
                    frame.replaced(child, result.replacement)
                    extend_body(body, result.replacement)
                    # nested composite was not completely removed
                    if child in composites:
                        all_composites_removed = False

            # all children were extracted or all composites were removed without any effects
            # left and no outputs (so no way for outer dependencies), drop this logical
            if not body or (all_composites_removed and not any([isinstance(t, helpers.EFFECTS) for t in body]) and not frame.task_outputs(task)):
                return Flatten.HandleResult(None)

            # now process the rewritten body
            groups = group_tasks(body.list, {
                "outputs": ir.Output,
                "updates": ir.Update,
                "aggregates": ir.Aggregate,
                "ranks": ir.Rank,
            })

            # if there are outputs, currently assume it's already at top level, so just return
            # the rewritten body
            if groups["outputs"]:
                return Flatten.HandleResult(ir.Logical(task.engine, task.hoisted, tuple(body), task.annotations))

            # if there are updates, extract as a new top level rule
            if groups["updates"]:
                # add dependencies for the logical, which is in the parent frame
                if frame._parent_frame:
                    body = frame._parent_frame.task_dependencies(task) | body
                ctx.top_level.append(ir.Logical(task.engine, task.hoisted, tuple(body), task.annotations))

                # no need to refer to the extracted logical because it is an update
                return Flatten.HandleResult(None, cast(OrderedSet[ir.Update], groups["updates"]))

            if groups["aggregates"]:
                if len(groups["aggregates"]) > 1:
                    # stop rewritting as we don't know how to handle this yet
                    return Flatten.HandleResult(task)

                # there must be only one
                agg = cast(ir.Aggregate, groups["aggregates"].some())

                # add agg dependencies to the body
                body = frame.task_dependencies(agg) | body

                # extract a new logical for the aggregate, exposing aggregate group-by and results
                exposed_vars = OrderedSet.from_iterable(list(agg.group) + helpers.aggregate_outputs(agg))
                connection = metamodel_utils.extract(agg, body, exposed_vars.list, ctx)

                # return a reference to the connection relation
                reference = f.logical([f.lookup(connection, exposed_vars.list)], merge_var_list(exposed_vars.list, task.hoisted))
                return Flatten.HandleResult(reference)

            if groups["ranks"]:
                if len(groups["ranks"]) > 1:
                    # stop rewritting as we don't know how to handle this yet
                    return Flatten.HandleResult(task)

                # there must be only one
                rank = cast(ir.Rank, groups["ranks"].some())

                # add rank dependencies to the body
                body = frame.task_dependencies(rank) | body

                # extract a new logical for the rank, exposing rank group-by and results
                exposed_vars = OrderedSet.from_iterable(list(rank.group) + list(rank.args) + [rank.result])
                connection = metamodel_utils.extract(rank, body, exposed_vars.list, ctx)

                # return a reference to the connection relation
                reference = f.logical([f.lookup(connection, exposed_vars.list)], merge_var_list(exposed_vars.list, task.hoisted))
                return Flatten.HandleResult(reference)

            return Flatten.HandleResult(ir.Logical(task.engine, task.hoisted, tuple(body)))

    def handle_match(self, match: ir.Match, ctx: AnalysisContext):
        # TODO: how to deal with malformed input like this?
        if not match.tasks:
            return Flatten.HandleResult(match)

        frame = ctx.current_frame()
        body = frame.task_dependencies(match)
        outputs = frame.task_outputs(match)
        exposed_vars = (frame.task_inputs(match) | outputs).list

        connection = None
        reference = None

        for branch in match.tasks:
            # process the branch
            result = self.handle(branch, ctx)
            assert(result.replacement)
            frame.replaced(branch, result.replacement)

            branch_body: OrderedSet[ir.Task] = OrderedSet.from_iterable(body)
            extend_body(branch_body, result.replacement)
            if reference:
                branch_body.add(negate(reference, len(outputs)))
                branch_body = OrderedSet.from_iterable([f.union([f.logical(branch_body.list, match.hoisted), reference], match.hoisted)])
            connection = metamodel_utils.extract(branch, branch_body, exposed_vars, ctx, "match")
            reference = f.logical([f.lookup(connection, exposed_vars)], exposed_vars)

        return Flatten.HandleResult(reference)


    def handle_union(self, union: ir.Union, ctx: AnalysisContext):
        # TODO: how to deal with malformed input like this?
        if not union.tasks:
            return Flatten.HandleResult(union)

        frame = ctx.current_frame()
        body = frame.task_dependencies(union)
        outputs = frame.task_outputs(union)
        exposed_vars = (frame.task_inputs(union) | outputs).list

        connection = None

        for branch in union.tasks:
            # process the branch
            result = self.handle(branch, ctx)
            if result.replacement:
                # the branch has some replacement, add it to the body to derive the union
                frame.replaced(branch, result.replacement)
                branch_body: OrderedSet[ir.Task] = OrderedSet.from_iterable(body)
                extend_body(branch_body, result.replacement)
            else:
                # the branch was extracted as updates, generate a body that derives the
                # union when any of the updates is done
                assert(result.updates)
                branch_body = ordered_set()
                for update in result.updates:
                    branch_body.add(ir.Lookup(union.engine, update.relation, wildcards(update.relation)))

            if connection is None:
                # first branch, extract making a connection relation
                connection = metamodel_utils.extract(branch, branch_body, exposed_vars, ctx, "union")
            else:
                # subsequent branch, extract reusing the connection relation
                # add derivation to the extracted body
                branch_body.add(f.derive(connection, exposed_vars))

                # extract the body
                ctx.top_level.append(ir.Logical(union.engine, tuple(), tuple(branch_body)))

        # return a reference to the connection
        assert(connection)
        reference = f.logical([f.lookup(connection, exposed_vars)], exposed_vars)
        return Flatten.HandleResult(reference)

    def handle_require(self, req: ir.Require, ctx: AnalysisContext):
        # only extract the domain if it is a somewhat complex Logical and there's more than
        # one check, otherwise insert it straight into all checks
        domain = req.domain
        if len(req.checks) > 1 and isinstance(domain, ir.Logical) and len(domain.body) > 1:
            body = OrderedSet.from_iterable(domain.body)
            vars = helpers.hoisted_vars(domain.hoisted)
            connection = metamodel_utils.extract(req, body, vars, ctx, "domain")
            domain = f.logical([f.lookup(connection, vars)], vars)

        for check in req.checks:
            # only generate logic for checks that have errors
            if check.error:
                handled_check_result = self.handle(check.check, ctx)
                if handled_check_result.replacement:
                    body = ordered_set()
                    body.add(domain)
                    body.add(ir.Not(req.engine, handled_check_result.replacement))
                    if (isinstance(check.error, ir.Logical)):
                        body.update(check.error.body)
                    else:
                        # this is more general but may trip the current splinter
                        body.add(check.error)
                    ctx.top_level.append(ir.Logical(req.engine, tuple(), tuple(body)))

        # currently we just drop the Require, but we should keep it here and link the
        # extracted logicals to it
        return Flatten.HandleResult(None)


#--------------------------------------------------
# Helpers
#--------------------------------------------------

def wildcards(relation: ir.Relation):
    return tuple([f.wild() for _ in relation.fields])

def extractable(t: ir.Task):
    """
    Whether this task is a Logical that will be extracted as a top level by this
    pass, because it has an aggregation, effects, match, union, etc.
    """
    extractable_types = (ir.Update, ir.Aggregate, ir.Match, ir.Union, ir.Rank)
    return isinstance(t, ir.Logical) and len(visitor.collect_by_type(extractable_types, t)) > 0

def extractables(composites: OrderedSet[ir.Task]):
    """ Filter the set of composites, keeping only the extractable ones. """
    return list(filter(extractable, composites))

def negate(reference: ir.Logical, values: int):
    """
    Return a negation of this reference, where the last `values` arguments are to
    be replaced by wildcards (i.e. len(reference.args) - values are keys so they need
    to be bound in the Not.)
    """
    lookup = cast(ir.Lookup, reference.body[0])
    args = []
    i = 0
    last = len(lookup.args) - values
    for arg in lookup.args:
        args.append(f.wild()) if i >= last else args.append(arg)
        i += 1

    return ir.Not(reference.engine, f.lookup(lookup.relation, args))

def merge_var_list(vars: list[ir.Var], hoisted: tuple[ir.VarOrDefault, ...]) -> list[ir.VarOrDefault]:
    """ Merge vars and hoisted, making sure that hoisted vars have precedence since they may have defaults. """
    r = []
    hoisted_vars = helpers.hoisted_vars(hoisted)
    for v in vars:
        if v not in hoisted_vars:
            r.append(v)
    r.extend(hoisted)
    return r

def extend_body(body: OrderedSet[ir.Task], extra: ir.Task):
    """ Add the extra task to the body, but if the extra is a simple logical, just
    inline its subtasks. """
    if isinstance(extra, ir.Logical):
        if extra.hoisted:
            # hoists, remove things that are already in the body to avoid duplicates
            logical_body = []
            for t in extra.body:
                if t not in body:
                    logical_body.append(t)
            if len(logical_body) == len(extra.body):
                # no duplicates
                body.add(extra)
            else:
                # some duplicate, remove them
                body.add(ir.Logical(
                    extra.engine,
                    extra.hoisted,
                    tuple(logical_body)
                ))
        else:
            # no hoists, just inline
            body.update(extra.body)
    else:
        body.add(extra)
