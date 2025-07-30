from __future__ import annotations

from typing import Optional, Sequence as PySequence, cast

from relationalai.early_access.metamodel import ir, compiler as c, factory as f, types, util
from relationalai.early_access.metamodel.helpers import collect_implicit_vars

class Splinter(c.Pass):
    """
    Splits multi-headed rules into multiple rules. Additionally, infers missing Exists tasks.
    """
    def rewrite(self, model: ir.Model, cache) -> ir.Model:
        if isinstance(model.root, ir.Logical):
            final = []
            new_relations:list[ir.Relation] = []
            new_relations.extend(model.relations)
            for child in model.root.body:
                new_logicals, relation = self.split(cast(ir.Logical, child))
                final.extend(new_logicals)
                if relation:
                    new_relations.append(relation)
            return ir.Model(
                    model.engines,
                    util.FrozenOrderedSet.from_iterable(new_relations),
                    model.types,
                    ir.Logical(
                        model.root.engine,
                        model.root.hoisted,
                        tuple(final)
                    )
                )
        return model

    def split(self, node: ir.Logical) -> tuple[list[ir.Logical], Optional[ir.Relation]]:
        # Split this logical, which represents a rule, into potentially many logicals, one
        # for each head (update or output)
        effects, body = self.split_items(node.body)
        if not body:
            return [node], None

        effects_vars = collect_implicit_vars(*effects)

        if len(effects) > 1:
            connection = f.relation(f"q{node.id}", [f.field("", types.Any) for v in effects_vars])
            final:list[ir.Logical] = [f.logical([*body, f.derive(connection, list(effects_vars))])]
            for effect in effects:
                effect_vars = collect_implicit_vars(effect)
                lookup_vars = [(v if v in effect_vars else f.wild(v.type)) for v in effects_vars]
                final.append(f.logical([f.lookup(connection, lookup_vars), effect]))
            return final, connection
        return [node], None


    def split_items(self, items: PySequence[ir.Task]) -> tuple[list[ir.Task], list[ir.Task]]:
        effects = []
        body = []
        for item in items:
            if isinstance(item, (ir.Update, ir.Output)):
                effects.append(item)
            else:
                body.append(item)
        return effects, body
