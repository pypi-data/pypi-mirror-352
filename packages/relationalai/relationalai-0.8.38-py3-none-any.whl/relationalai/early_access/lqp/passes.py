from relationalai.early_access.metamodel.compiler import Pass
from relationalai.early_access.metamodel import ir, builtins as rel_builtins, factory as f, visitor
from relationalai.early_access.metamodel.typer.checker import Checker
from relationalai.early_access.metamodel.typer.typer2 import InferTypes
from typing import cast, Union
from relationalai.early_access.metamodel import types

from relationalai.early_access.metamodel.rewrite import Splinter, GarbageCollectNodes

# TODO: Move this into metamodel.rewrite
from relationalai.early_access.rel.rewrite import Flatten, QuantifyVars, ExtractCommon, CDC

import datetime

def lqp_passes() -> list[Pass]:
    return [
        Checker(),
        InferTypes(),
        GarbageCollectNodes(),
        CDC(),
        ExtractCommon(),
        Flatten(),
        QuantifyVars(),
        Splinter(), # Adds missing existentials + splits multi-headed rules into single rules
        UnifyDefinitions(),
        EliminateData(),  # Turns Data nodes into ordinary relations.
        EliminateValueTypeConstants(),
    ]

class UnifyDefinitions(Pass):
    def rewrite(self, model: ir.Model, cache) -> ir.Model:
        multidef_relations = self.get_multidef_relations(model)
        for relation in multidef_relations:
            model = self.rename_multidef(model, relation)
        return model

    def get_multidef_relations(self, model: ir.Model) -> set[ir.Relation]:
        seen = set()
        result = set()
        root = cast(ir.Logical, model.root)
        for task in root.body:
            task = cast(ir.Logical, task)
            for subtask in task.body:
                if isinstance(subtask, ir.Update):
                    assert subtask.effect == ir.Effect.derive, "only derive updates supported yet"
                    name = subtask.relation
                    if name.id in seen:
                        result.add(name)
                    seen.add(name.id)
        return result

    def rename_multidef(self, model: ir.Model, relation: ir.Relation) -> ir.Model:
        defname = relation.name
        root = cast(ir.Logical, model.root)
        new_subtasks = []
        new_relations = []
        total_ct = 0
        for subtask in root.body:
            subtask = cast(ir.Logical, subtask)
            new_subsubtasks: list[ir.Task] = []
            for subsubtask in subtask.body:
                if isinstance(subsubtask, ir.Update):
                    assert subsubtask.effect == ir.Effect.derive, "only derive updates supported yet"
                    name = subsubtask.relation
                    if name.id == relation.id:
                        total_ct += 1
                        # TODO: this needs to be unique btw (gensym)
                        new_name = f"{defname}_{total_ct}"
                        new_subsubtask = self.rename_relation(subsubtask, new_name)
                        new_subsubtasks.append(new_subsubtask)
                        new_relation = ir.Relation(
                            new_name,
                            relation.fields,
                            relation.requires,
                        )
                        new_relations.append(new_relation)
                    else:
                        new_subsubtasks.append(subsubtask)
                else:
                    new_subsubtasks.append(subsubtask)

            new_subtask = ir.Logical(
                subtask.engine,
                subtask.hoisted,
                tuple(new_subsubtasks),
            )
            new_subtasks.append(new_subtask)
        assert total_ct > 0, f"should have found at least one definition for {defname}"

        args = []
        for field in relation.fields:
            args.append(ir.Var(field.type, field.name))

        # Also add the new definition
        final_relation = ir.Relation(
            defname,
            relation.fields,
            relation.requires,
        )
        new_update = ir.Update(
            root.engine,
            final_relation,
            tuple(args),
            ir.Effect.derive,
        )

        logical_tasks = []
        lookups = []
        for new_relation in new_relations:
            new_lookup = ir.Lookup(
                root.engine,
                new_relation,
                tuple(args),
            )
            lookups.append(new_lookup)

        disj = ir.Union(
            root.engine,
            tuple(),
            tuple(lookups),
        )
        logical_tasks.append(disj)
        logical_tasks.append(new_update)
        new_logical = ir.Logical(
            root.engine,
            root.hoisted,
            tuple(logical_tasks),
        )
        new_subtasks.append(new_logical)

        new_root = ir.Logical(root.engine, root.hoisted, tuple(new_subtasks))
        model = ir.Model(
            model.engines,
            model.relations | new_relations,
            model.types,
            new_root,
        )
        return model

    def rename_relation(self, task: ir.Update, new_name: str) -> ir.Update:
        assert isinstance(task, ir.Update)
        assert task.effect == ir.Effect.derive, "only derive updates supported yet"
        old_relation = task.relation
        new_relation = ir.Relation(
            new_name,
            old_relation.fields,
            old_relation.requires,
        )
        new_task = ir.Update(
            task.engine,
            new_relation,
            task.args,
            task.effect,
        )
        return new_task

# We don't have a proto representation for these, so we rewrite them to be constructed directly
class EliminateValueTypeConstants(Pass):
    def rewrite(self, model: ir.Model, cache) -> ir.Model:
        p = RewriteBadLiterals()
        return p.walk(model)

def rewrite_bad_literals(self, args):
    vars_to_existify = []
    new_conjs = []
    new_args = []

    for arg in args:
        if isinstance(arg, datetime.datetime):
            new_var = f.var("dt_var", types.DateTime)
            new_args.append(new_var)
            vars_to_existify.append(new_var)

            year = arg.year
            month = arg.month
            day = arg.day
            hour = arg.hour
            minute = arg.minute
            second = arg.second

            lookup = f.lookup(
                    rel_builtins.construct_datetime,
                    tuple([
                        f.literal(year),
                        f.literal(month),
                        f.literal(day),
                        f.literal(hour),
                        f.literal(minute),
                        f.literal(second),
                        new_var,
                    ])
                )
            new_conjs.append(lookup)
        elif isinstance(arg, datetime.date):
            new_var = f.var("dt_var", types.Date)
            new_args.append(new_var)
            vars_to_existify.append(new_var)

            year = arg.year
            month = arg.month
            day = arg.day

            lookup = f.lookup(
                    rel_builtins.construct_date,
                    tuple([
                        f.literal(year),
                        f.literal(month),
                        f.literal(day),
                        new_var,
                    ])
                )
            new_conjs.append(lookup)
        else:
            new_args.append(arg)

    return new_args, vars_to_existify, new_conjs

class RewriteBadLiterals(visitor.Rewriter):
    def handle_lookup(self, node: ir.Lookup, parent: ir.Node) -> Union[ir.Lookup, ir.Exists]:
        args = node.args
        new_args, vars_to_existify, new_conjs = rewrite_bad_literals(self, args)

        if len(vars_to_existify) == 0:
            return node

        new_lookup = f.lookup(
            node.relation,
            tuple(new_args),
        )
        new_conjs.append(new_lookup)

        result = f.exists(
            vars_to_existify,
            f.logical(tuple(new_conjs)),
        )

        return result

    def handle_output(self, node: ir.Output, parent: ir.Node) -> Union[ir.Output, ir.Logical]:
        args = [v[1] for v in node.aliases]
        new_args, vars_to_existify, new_conjs = rewrite_bad_literals(self, args)

        if len(vars_to_existify) == 0:
            return node

        new_aliases = []
        for i, alias in enumerate(node.aliases):
            new_aliases.append((alias[0], new_args[i]))

        new_output = node.reconstruct(aliases=tuple(new_aliases))
        new_conjs.append(new_output)

        return f.logical(new_conjs)

    def handle_update(self, node: ir.Update, parent: ir.Node) -> Union[ir.Update, ir.Logical]:
        args = node.args
        new_args, vars_to_existify, new_conjs = rewrite_bad_literals(self, args)

        if len(vars_to_existify) == 0:
            return node

        new_update = node.reconstruct(args=tuple(new_args))
        new_conjs.append(new_update)
        return f.logical(new_conjs)

# Creates intermediary relations for all Data nodes and replaces said Data nodes
# with a Lookup into these created relations.
class EliminateData(Pass):
    def rewrite(self, model: ir.Model, cache) -> ir.Model:
        r = self.DataRewriter()
        return r.walk(model)

    # Does the actual work.
    class DataRewriter(visitor.Rewriter):
        new_relations: list[ir.Relation]
        new_updates: list[ir.Logical]
        # Counter for naming new relations.
        # It must be that new_count == len new_updates == len new_relations.
        new_count: int

        def __init__(self):
            self.new_relations = []
            self.new_updates = []
            self.new_count = 0
            super().__init__()

        # Create a new intermediary relation representing the Data (and pop it in
        # new_updates/new_relations) and replace this Data with a Lookup of said
        # intermediary.
        def handle_data(self, node: ir.Data, parent: ir.Node) -> ir.Lookup:
            self.new_count += 1
            intermediary_name = f"formerly_Data_{self.new_count}"

            intermediary_relation = f.relation(
                intermediary_name,
                [f.field(v.name, v.type) for v in node.vars]
            )
            self.new_relations.append(intermediary_relation)

            intermediary_update = f.logical([
                # For each row (union), equate values and their variable (logical).
                f.union(
                    [
                        f.logical(
                            [
                                f.lookup(rel_builtins.eq, [val, var])
                                for (val, var) in zip(row, node.vars)
                            ],
                            hoisted = node.vars,
                        )
                        for row in node
                    ],
                    hoisted = node.vars,
                ),
                # And pop it back into the relation.
                f.update(intermediary_relation, node.vars, ir.Effect.derive),
            ])
            self.new_updates.append(intermediary_update)

            replacement_lookup = f.lookup(intermediary_relation, node.vars)

            return replacement_lookup

        # Walks the model for the handle_data work then updates the model with
        # the new state.
        def handle_model(self, model: ir.Model, parent: None):
            walked_model = super().handle_model(model, parent)
            assert len(self.new_relations) == len(self.new_updates) and self.new_count == len(self.new_relations)

            # This is okay because its LQP.
            assert isinstance(walked_model.root, ir.Logical)
            root_logical = cast(ir.Logical, walked_model.root)

            # We may need to add the new intermediaries from handle_data to the model.
            if self.new_count  == 0:
                return model
            else:
                return ir.Model(
                    walked_model.engines,
                    walked_model.relations | self.new_relations,
                    walked_model.types,
                    ir.Logical(
                        root_logical.engine,
                        root_logical.hoisted,
                        root_logical.body + tuple(self.new_updates),
                        root_logical.annotations,
                    ),
                    walked_model.annotations,
                )
