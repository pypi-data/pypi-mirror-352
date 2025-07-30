from __future__ import annotations

from relationalai.early_access.metamodel import ir, factory as f, builtins as bt, types
from relationalai.early_access.metamodel.compiler import Pass
from relationalai.early_access.metamodel.util import OrderedSet, ordered_set
from relationalai.early_access.rel import builtins as rel_bt
from relationalai.early_access.rel.dependency import AnalysisContext, ctx_frame

class CDC(Pass):
    """
    Pass to process tables brought to Relational AI logical engines by CDC. When CDC occurs,
    wide snowflake tables are shredded into smaller tables. This pass ensures that code that
    reads from the wide relation is changed to read from the smaller tables. Furthermore,
    it attaches the @function annotation to the property lookups, as an optimization.

    Beware that this pass makes assumptions about the names and types of CDC relations and
    columns!

    From:
        Logical
            TPCH.SF1.LINEITEM(l_orderkey, l_partkey, l_suppkey, l_linenumber, l_quantity, l_extendedprice, l_discount, l_tax, l_returnflag, l_linestatus, l_shipdate, l_commitdate, l_receiptdate, l_shipinstruct, l_shipmode, l_comment)
            construct(LineItem, "l_orderkey", l_orderkey, "l_linenumber", l_linenumber, lineitem)
            -> derive LineItem(lineitem)
            -> derive l_orderkey(lineitem, l_orderkey)
            -> derive l_linenumber(lineitem, l_linenumber)
    To:
    Logical
        tpch_sf1_lineitem("L_ORDERKEY", row_id, l_orderkey)
        tpch_sf1_lineitem("L_LINENUMBER", row_id, l_linenumber)
        construct(LineItem, "l_orderkey", l_orderkey, "l_linenumber", l_linenumber, lineitem)
        -> derive LineItem(lineitem)
        -> derive l_orderkey(lineitem, l_orderkey) (@function)
        -> derive l_linenumber(lineitem, l_linenumber) (@function)
    """

    #--------------------------------------------------
    # Public API
    #--------------------------------------------------
    def rewrite(self, model: ir.Model, cache) -> ir.Model:
        # create the dependency analysis context
        ctx = CDC.RewriteContext(model)

        # rewrite the root
        replacement = self.handle(model.root, ctx)

        # the new root contains the extracted top level logicals and the rewritten root
        if ctx.analysis_ctx.top_level:
            new_root = ir.Logical(model.root.engine, tuple(), tuple(ctx.analysis_ctx.top_level + [replacement]))
        else:
            new_root = replacement

        # create the new model, updating relations and root
        return ir.Model(
            model.engines,
            OrderedSet.from_iterable(model.relations).update(ctx.analysis_ctx.relations).frozen(),
            model.types,
            new_root
        )

    class RewriteContext():
        def __init__(self, model: ir.Model):
            self.analysis_ctx = AnalysisContext(model.root)
            self.cdc_relations = dict()

    #--------------------------------------------------
    # IR handlers
    #--------------------------------------------------

    def handle(self, task: ir.Task, ctx: CDC.RewriteContext):
        # currently we only extract if it's a sequence of Logicals, but we could in the
        # future support other intermediate nodes
        if isinstance(task, ir.Logical):
            return self.handle_logical(task, ctx)
        else:
            return task

    def handle_logical(self, task: ir.Logical, ctx: CDC.RewriteContext):

        wide_cdc_table_lookups = ordered_set()
        for child in task.body:
            if isinstance(child, ir.Lookup) and bt.from_cdc_annotation in child.relation.annotations:
                wide_cdc_table_lookups.add(child)

        # optimization to avoid creating a frame if unnecessary
        if not wide_cdc_table_lookups:
            # no need to analyze dependencies, just handle children recursively and
            # reconstruct the logical
            body:OrderedSet[ir.Task] = ordered_set()
            for child in task.body:
                body.add(self.handle(child, ctx))
            return ir.Logical(task.engine, task.hoisted, tuple(body), task.annotations)

        # ensure function annotation is in the model
        ctx.analysis_ctx.relations.append(rel_bt.function)

        # create frame to process the children
        with ctx_frame(ctx.analysis_ctx, task):
            body:OrderedSet[ir.Task] = ordered_set()

            # find variables required by the other tasks
            required_vars = ordered_set()
            for child in task.body:
                if child not in wide_cdc_table_lookups:
                    required_vars.update(ctx.analysis_ctx.bindings.get_inputs(child))

            # rewrite the cdc lookup table into lookups for each required variable
            for child in task.body:
                if child in wide_cdc_table_lookups:
                    assert isinstance(child, ir.Lookup)
                    wide_relation = child.relation
                    properties = ctx.analysis_ctx.bindings.get_outputs(child) & required_vars
                    if properties:
                        assert isinstance(child.args[0], ir.Var) and child.args[0].type == types.RowId
                        row_id = child.args[0]
                        for property in properties:
                            if property.type == types.RowId and len(properties) > 1:
                                continue

                            relation = self._get_property_cdc_relation(wide_relation, property, ctx)
                            field_name = ir.Literal(types.Symbol, property.name)
                            if property.type == types.RowId:
                                # TODO: eventually we should use METADATA&KEY instead of METADATA$ROW_ID
                                # but I don't think we force migrated all streams to it yet
                                field_name = ir.Literal(types.Symbol, "METADATA$ROW_ID")
                                property = ir.Var(type=types.RowId, name=property.name)

                            body.add(ir.Lookup(
                                task.engine,
                                relation,
                                tuple([field_name, row_id, property])
                            ))

            # handle non cdc table children, adding @function to the updates
            for child in task.body:
                if child not in wide_cdc_table_lookups:
                    replacement = self.handle(child, ctx)
                    if isinstance(replacement, ir.Update):
                        if len(replacement.args) == 1:
                            body.add(replacement)
                        else:
                            body.add(replacement.reconstruct(
                                replacement.engine,
                                replacement.relation,
                                replacement.args,
                                replacement.effect,
                                replacement.annotations | [rel_bt.function_annotation]
                            ))
                    else:
                        body.add(replacement)

            return ir.Logical(task.engine, task.hoisted, tuple(body), task.annotations)

    def _get_property_cdc_relation(self, wide_cdc_relation: ir.Relation, property: ir.Var, ctx: CDC.RewriteContext):
        """
        Get the relation that represents this property var in this wide_cdc_relation. If the
        relation is not yet available in the context, this method will create and register it.
        """
        relation_name = wide_cdc_relation.name.lower().replace(".", "_")
        key = (relation_name, property.name)
        if key not in ctx.cdc_relations:
            # the property relation is overloaded for all properties of the same wide cdc relation, so they have
            # the same name, but potentially a different type in the value column; also note that they are
            # annotated as external to avoid renaming.
            relation = f.relation(
                relation_name,
                [f.field("symbol", types.Symbol), f.field("row_id", types.Number), f.field("value", property.type)],
                annos=[bt.external_annotation]
            )
            ctx.cdc_relations[key] = relation
            ctx.analysis_ctx.relations.append(relation)
        return ctx.cdc_relations[key]
