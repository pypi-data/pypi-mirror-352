from collections import defaultdict
from relationalai.early_access.dsl.adapters.orm.model import ExclusiveInclusiveSubtypeFact, ExclusiveSubtypeFact
from relationalai.early_access.dsl.adapters.orm.parser import ORMParser
from relationalai.early_access.dsl.orm.models import Model
from relationalai.early_access.builder import Integer, String
from relationalai.early_access.builder.builder import DateTime, Decimal, Date
from relationalai.early_access.dsl.orm.utils import build_relation_name_from_reading


class ORMAdapterQB:

    def __init__(self, orm_file_path: str):
        self._parser = ORMParser(orm_file_path)
        self._relationship_role_value_constraints = defaultdict()
        self._relationships = {}
        self.model = self.orm_to_model()

    def orm_to_model(self):
        model = Model(self._parser.model_name())

        self._add_value_types(model)
        self._add_entity_types(model)
        self._add_subtype_relationships(model)
        self._add_relationships(model)
        self._add_external_identifying_relationships(model)
        self._add_role_value_constraints(model)
        self._add_role_constraints(model)
        return model

    def _add_value_types(self, model):
        for vt in self._parser.value_types().values():
            model.Concept(vt.name, extends=[self._map_datatype(vt.data_type)])

    def _add_entity_types(self, model):
        extended_concepts = [y.subtype_name for x in self._parser.subtype_facts().values() for y in x]

        for et in self._parser.entity_types().values():
            if et.name not in extended_concepts:
                model.Concept(et.name)

        subtype_facts = self._parser.sorted_subtype_facts()
        for st_fact in subtype_facts:
            parent = st_fact.supertype_name
            parent_entity = model.lookup_concept(parent)
            if parent_entity is None:
                parent_entity = model.Concept(parent)
            model.Concept(st_fact.subtype_name, extends=[parent_entity])

    def _add_subtype_relationships(self, model):
        for parent, children in self._parser.subtype_facts().items():
            exclusives = []
            exclusives_and_inclusives = []
            for child in children:
                sub = model.lookup_concept(child.subtype_name)
                if isinstance(child, ExclusiveInclusiveSubtypeFact):
                    exclusives_and_inclusives.append(sub)
                elif isinstance(child, ExclusiveSubtypeFact):
                    exclusives.append(sub)

            if len(exclusives_and_inclusives) > 0:
                model.exclusive_subtype_constraint(*exclusives_and_inclusives)
                model.inclusive_subtype_constraint(*exclusives_and_inclusives)
            if len(exclusives) > 0:
                model.exclusive_subtype_constraint(*exclusives)

    def _add_relationships(self, model):
        object_types = self._parser.object_types()
        unique_roles = self._parser.unique_roles()
        mandatory_roles = self._parser.mandatory_roles()
        role_value_constraints = self._parser.role_value_constraints()
        fact_type_to_internal_ucs = self._parser.fact_type_to_internal_ucs()
        fact_type_to_complex_ucs = self._parser.fact_type_to_complex_ucs()
        fact_type_to_roles = self._parser.fact_type_to_roles()
        for fact_type, reading_orders in self._parser.fact_type_readings().items():

            # Adding the main reading
            rdo = reading_orders[0]
            player = object_types[rdo.roles[0].role.player].name
            player_entity = model.lookup_concept(player)
            rel_name, reading = self._build_relation(model, fact_type, player_entity, rdo)
            relationship = model.Relationship(reading)
            setattr(player_entity, rel_name, relationship)
            self._relationships[fact_type] = relationship

            # Marking unique and mandatory roles
            role_idx_to_player = []
            for ro in rdo.roles:
                role_id = ro.role.id
                role_idx_to_player.append(role_id)
                role_index = role_idx_to_player.index(role_id)
                role = relationship[role_index]
                if role_id in unique_roles:
                    model.unique(role)
                if role_id in mandatory_roles:
                    model.mandatory(role)
                if role_id in role_value_constraints.keys():
                    self._relationship_role_value_constraints[role] = role_value_constraints[role_id]

            # Adding alternative readings
            if len(reading_orders) > 1:
                for rdo in reading_orders[1:]:
                    other_player = object_types[rdo.roles[0].role.player].name
                    other_player_entity = model.lookup_concept(other_player)
                    rel_name, alt_reading = self._build_relation(model, fact_type, other_player_entity, rdo)
                    setattr(other_player_entity, rel_name, relationship.alt(alt_reading))

            # Marking identifying relationships
            if fact_type in fact_type_to_internal_ucs:
                for uc in fact_type_to_internal_ucs[fact_type]:
                    if uc.identifies:
                        player_entity.identify_by(relationship)

            # Adding constraint spanning over multiple roles
            if fact_type in fact_type_to_complex_ucs:
                for uc in fact_type_to_complex_ucs[fact_type]:
                    uc_roles = []
                    for role in fact_type_to_roles[fact_type]:

                        if role.id in uc.roles:
                            p = role.id
                            rl = role_idx_to_player.index(p)
                            uc_roles.append(self._relationships[fact_type][rl])
                    model.unique(*uc_roles)

    def _add_external_identifying_relationships(self, model):
        roles = self._parser.roles()
        fact_types_to_readings = self._parser.fact_type_readings()
        object_types = self._parser.object_types()
        for uc_id, uc in self._parser.external_uniqueness_constraints().items():
            entity = model.lookup_concept(object_types[uc.identifies].name)
            identifying_rel = []
            for ro in uc.roles:
                fact_name = roles[ro].relationship_name
                readings = fact_types_to_readings[fact_name]
                for rdo in readings:
                    if rdo.roles[0].role.player == uc.identifies:
                        for rl in rdo.roles:
                            if rl.role.id == ro:
                                identifying_rel.append(self._relationships[fact_name])
            entity.identify_by(*identifying_rel)

    def _add_role_constraints(self, model):
        roles = self._parser.roles()
        object_types = self._parser.object_types()
        for rc in self._parser.role_constraints():
            constraint_roles = []
            for ro in rc.roles:
                role_obj = roles[ro]
                player_entity = model.lookup_concept(object_types[role_obj.player].name)
                rel = self._relationships[role_obj.relationship_name]
                idx = rel._field_names.index(player_entity._name.lower())
                constraint_roles.append(rel[idx])
            if rc.inclusive:
                model.inclusive_roles(*constraint_roles)
            if rc.exclusive:
                model.exclusive_roles(*constraint_roles)

    def _add_role_value_constraints(self, model):
        for rel, values in self._relationship_role_value_constraints.items():
            model.role_value_constraint(rel, values)

    def _build_reading(self, model, reading_order):
        object_types = self._parser.object_types()
        rel_args = []
        for rdo_role in reading_order.roles:
            if rdo_role.prefix is not None:
                rel_args.append(rdo_role.prefix + "-")
            p = model.lookup_concept(object_types[rdo_role.role.player].name)
            rel_args.append(f"{{{p}}}") if rdo_role.role.name == "" else rel_args.append(f"{{{rdo_role.role.name}:{p}}}")
            if rdo_role.postfix is not None:
                rel_args.append("-" + rdo_role.postfix)
            if rdo_role.text is not None:
                rel_args.append(" " + rdo_role.text + " ")
        return ''.join(rel_args).strip()

    def _rename_to_ref_mode(self, model, first_player_entity, fact_type):
        identifier_fact_type_to_entity_type = self._parser.identifier_fact_type_to_entity_type()
        entity_type = identifier_fact_type_to_entity_type.get(fact_type)
        if entity_type:
            player = model.lookup_concept(entity_type.name)
            if first_player_entity == player:
                return entity_type.ref_mode
        return None

    def _build_relation(self, model, fact_type, player_entity, reading_order):
        object_types = self._parser.object_types()
        role_name = ""
        for role in reading_order.roles:
            if object_types[role.role.player].name != player_entity._name:
                role_name = role.role.name
        reading = self._build_reading(model, reading_order)
        ref_mode = self._rename_to_ref_mode(model, player_entity, fact_type)
        if ref_mode is not None:
            rel_name = ref_mode.lower()
        else:
            rel_name = role_name if role_name != "" else build_relation_name_from_reading(reading)
        return rel_name, reading

    @staticmethod
    def _map_datatype(dt):
        mapping = {
            "AutoCounterNumericDataType": Integer,
            # TODO  must be changed to UnsignedInt when available
            "UnsignedIntegerNumericDataType": Integer,
            "VariableLengthTextDataType": String,
            "DateAndTimeTemporalDataType": DateTime,
            "DecimalNumericDataType": Decimal,
            "DateTemporalDataType": Date
        }
        return mapping.get(dt, String)
