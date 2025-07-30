# pyright: reportArgumentType=false
from itertools import product
from types import MappingProxyType
from typing import cast, Union, Optional

from relationalai.early_access.dsl.bindings.tables import (Binding, IdentifierBinding, RoleBinding,
                                                           FilteringSubtypeBinding, SubtypeBinding, BindableColumn,
                                                           DEFAULT_DECIMAL_SCALE, DEFAULT_DECIMAL_SIZE)
from relationalai.early_access.dsl.codegen.common import PotentiallyBoundRelationship, BoundExternalPreferredUC
from relationalai.early_access.dsl.codegen.reasoner import Reasoner
from relationalai.early_access.dsl.codegen.relations import EntityMap, ValueMap, EntitySubtypeMap, RoleMap, \
    CompositeEntityMap
from relationalai.early_access.dsl.core import std
from relationalai.early_access.dsl.core.namespaces import Namespace
from relationalai.early_access.dsl.core.relations import rule, AbstractRelation, Relation, EntityInstanceRelation
from relationalai.early_access.dsl.core.rules import Annotation, Vars
from relationalai.early_access.dsl.core.types import AbstractValueType
from relationalai.early_access.dsl.core.types import Type
from relationalai.early_access.dsl.core.types.constrained.nominal import ValueType
from relationalai.early_access.dsl.core.types.standard import RowId, Decimal, Integer, Symbol, Float
from relationalai.early_access.dsl.core.utils import camel_to_snake
from relationalai.early_access.dsl.ontologies.relationships import Reading
from relationalai.early_access.dsl.ontologies.roles import Role
from relationalai.early_access.dsl.types.entities import EntityType
from relationalai.early_access.metamodel.util import OrderedSet


DEFAULT_WEAVER_CONFIG = MappingProxyType({
    'decimal_size': DEFAULT_DECIMAL_SIZE,
    'decimal_scale': DEFAULT_DECIMAL_SCALE,
})


class Weaver:

    def __init__(self, model, config=None):
        self._model = model
        self._config = config or DEFAULT_WEAVER_CONFIG
        self._reasoner = Reasoner(model)

        # Physical Relations & Classification
        self._relations: dict[str, 'AbstractRelation'] = {}
        self._preferred_id_relations: OrderedSet['AbstractRelation'] = OrderedSet()
        self._identifier_relations: OrderedSet['Relation'] = OrderedSet()
        self._entity_map_relations: OrderedSet['Relation'] = OrderedSet()
        self._subtype_entity_map_relations: OrderedSet['AbstractRelation'] = OrderedSet()
        self._value_map_relations: OrderedSet['Relation'] = OrderedSet()
        self._entity_population_relations: OrderedSet['Relation'] = OrderedSet()

        self._binding_to_value_map: dict['Binding', 'ValueMap'] = {}
        self._constructor_binding_to_value_map: dict['Binding', 'EntityMap'] = {}
        self._entity_to_id_relations: dict['EntityType', 'AbstractRelation'] = {}
        self._concept_to_identifies_relations: dict['Type', 'AbstractRelation'] = {}
        self._subtype_to_entity_map: dict['EntityType', list['EntitySubtypeMap']] = {}
        self._composite_entity_to_entity_maps: dict['EntityType', list['CompositeEntityMap']] = {}

    def generate(self):
        self._reasoner.analyze()
        self._generate_value_maps()
        self._generate_entity_maps()
        self._generate_composite_entity_maps()
        self._generate_subtype_entity_maps()
        self._generate_entity_populations()
        self._generate_non_identifier_relationships()

    def _value_converter(self, col: BindableColumn) -> Optional[AbstractRelation]:
        if col.type() != Decimal:
            return None

        size = col.decimal_size()
        scale = col.decimal_scale()
        if size is None or scale is None:
            raise ValueError(f'Decimal column {col.physical_name()} must have size and scale defined')

        if size == self._cfg_decimal_size() and scale == self._cfg_decimal_scale():
            return None

        return self._ref_decimal_convert(size, scale)

    def _ref_decimal_convert(self, size: int, scale: int):
        fqn = self._fqn_decimal_convert(size, scale)
        rel = self._relations.get(fqn)
        if rel is None:
            rel = self._model.external_relation(fqn, Decimal, Decimal)
            unpack_decimal = std.unpack(Decimal, Symbol, Symbol, Symbol, Integer)
            with rel:
                @rule(Annotation.INLINE)
                def decimal_convert(raw, rez):
                    name, t_bits, t_decimals, int_val, bits, decimals, div, float_rez = Vars(
                        Symbol, Symbol, Symbol, Integer, Integer, Integer, Integer, Float
                    )
                    unpack_decimal(raw, name, t_bits, t_decimals, int_val)
                    std.mirror_lower(t_bits, bits)
                    std.mirror_lower(t_decimals, decimals)
                    std.power(10, decimals, div)
                    _= float_rez == int_val / div
                    std.new_decimal(self._cfg_decimal_size(), self._cfg_decimal_scale(), float_rez, rez)

            self._relations[fqn] = rel
        return rel

    def _fqn_decimal_convert(self, size: int, scale: int):
        return f'decimal_{size}_{scale}_to_{self._cfg_decimal_size()}_{self._cfg_decimal_scale()}_convert'

    def _generate_value_maps(self):
        for binding in self._reasoner.value_type_bindings():
            if not isinstance(binding, FilteringSubtypeBinding):
                self._gen_value_map(binding)

    def _generate_entity_maps(self):
        for binding in self._reasoner.constructor_bindings():
            self._gen_entity_map(binding)
            self._gen_preferred_id(binding)
        for binding in self._reasoner.referent_constructor_bindings():
            if not isinstance(binding, FilteringSubtypeBinding):
                self._gen_entity_map(binding)

    def _generate_composite_entity_maps(self):
        for bound_constraint in self._reasoner.bound_external_ucs():
            entity_map_combinations = self._get_entity_map_combinations_for_composite(bound_constraint)

            composite_emaps = []
            fqn = self._fqn_composite_entity_map(bound_constraint)
            concept = bound_constraint.concept
            for idx, entity_map_combination in enumerate(entity_map_combinations):
                rel_nm = f'{fqn}{idx}' if idx > 0 else fqn
                composite_emap = CompositeEntityMap(Namespace.top, rel_nm, RowId, concept, *entity_map_combination)
                composite_emaps.append(composite_emap)
                self._register_relation(fqn, composite_emap, self._entity_map_relations)
            self._composite_entity_to_entity_maps[concept] = composite_emaps

    def _get_entity_map_combinations_for_composite(self, bound_constraint: BoundExternalPreferredUC) -> list[list['EntityMap']]:
        # Start with the role bindings to build the combinations
        role_bindings = bound_constraint.role_bindings
        # Build a list of binding lists for each role in the right order
        role_binding_lists = [role_bindings[role] for role in bound_constraint.constraint.roles()]
        # Generate all possible combinations of bindings and convert each combination to a list
        all_combinations = [list(combination) for combination in product(*role_binding_lists)]  # pyright: ignore[reportCallIssue]
        # Construct entity map combinations using the _ref_entity_map method
        entity_map_combinations = [
            [self._ref_entity_map(binding, binding.role) for binding in combination]
            for combination in all_combinations
        ]
        return entity_map_combinations

    @staticmethod
    def _fqn_composite_entity_map(bound_constraint: BoundExternalPreferredUC):
        concept = bound_constraint.concept
        assert isinstance(concept, EntityType)
        concept_nm = camel_to_snake(concept.display())
        source_nm = bound_constraint.table.physical_name()
        return f'{concept_nm}__impl__{source_nm}_row_to_{concept_nm}'

    def _generate_subtype_entity_maps(self):
        for binding in self._reasoner.subtype_bindings():
            self._gen_subtype_entity_map(binding)

    def _generate_entity_populations(self):
        for entity_type, relation in self._entity_to_id_relations.items():
            self._gen_entity_population(entity_type, relation)
        for entity_type, relations in self._composite_entity_to_entity_maps.items():
            for relation in relations:
                self._gen_entity_population(entity_type, relation)
        for subtype, relations in self._subtype_to_entity_map.items():
            for relation in relations:
                self._gen_entity_population(subtype, relation)
        # add union population relations for those missing one
        for parent_type, subtypes in self._reasoner.subtype_map().items():
            self._gen_union_entity_population(parent_type, subtypes)

    def _gen_union_entity_population(self, parent_type: EntityType, subtypes: OrderedSet[EntityType]):
        has_no_identifier = self._model.identifier_of(parent_type) is None
        has_no_entity_map = parent_type not in self._subtype_to_entity_map
        if has_no_identifier and has_no_entity_map:
            for subtype in subtypes:
                with parent_type:
                    @rule()
                    def add_subtype_population(val):
                        subtype(val)

    def _generate_non_identifier_relationships(self):
        for rel_meta in self._reasoner.bound_relationships():
            if not self._reasoner.is_identifier_relationship(rel_meta.relationship):
                relationship = rel_meta.relationship
                if relationship.arity() >= 2:  # arity 2+ are semantic predicates
                    self._gen_semantic_predicate(rel_meta)

    def _gen_preferred_id(self, binding: Union[IdentifierBinding, SubtypeBinding]):
        # =
        # Simple case: a single role, hence the preferred id is the role itself.
        #
        # We generate the following rules:
        #
        #   def {concept}:id(v, c): ...
        # =
        ctor_role = self._reasoner.lookup_binding_role(binding)
        value_concept = ctor_role.player()
        val_role = ctor_role.sibling()
        assert val_role is not None
        entity_concept = val_role.player()

        # find the relations that have been created
        pref_id_relation = None
        identifies_relation = None
        for reading in ctor_role.part_of.readings():
            roles = reading.roles
            rel_name = reading.rel_name
            if roles[0] == ctor_role:
                if isinstance(value_concept, EntityType) or isinstance(value_concept, ValueType):
                    identifies_relation = getattr(value_concept, rel_name)
            else:
                assert isinstance(entity_concept, EntityType)
                pref_id_relation = entity_concept[rel_name]

        rel_nm = self._fqn_preferred_id(entity_concept)
        assert pref_id_relation is not None
        with pref_id_relation:
            @rule()
            def identifier(c, i):
                row = Vars(RowId)
                self._ref_value_map(binding)(row, i)
                self._ref_constructor_entity_map(binding)(row, c)
        self._register_relation(rel_nm, pref_id_relation, self._preferred_id_relations)
        self._entity_to_id_relations[entity_concept] = pref_id_relation

        # multiple bindings can exist, but we only need to transpose once
        rel_nm = self._fqn_identifies(value_concept)
        # TODO: fix this one below
        if isinstance(value_concept, AbstractValueType) and rel_nm not in self._relations:
            identifies_relation = self._model.external_relation(rel_nm, value_concept, entity_concept)
        assert identifies_relation is not None
        if identifies_relation not in self._identifier_relations:
            assert pref_id_relation is not None
            with identifies_relation:
                @rule()
                def identifies(i, c):
                    pref_id_relation(c, i)
            self._register_relation(rel_nm, identifies_relation, self._identifier_relations)
            self._concept_to_identifies_relations[value_concept] = identifies_relation

    @staticmethod
    def _fqn_preferred_id(concept: 'EntityType'):
        return f'{camel_to_snake(concept.display())}__id'

    def _ref_identifies(self, binding: 'Binding'):
        pid_ref = binding.column.references
        if pid_ref:
            concept = self._reasoner.referenced_concept(pid_ref)
        else:
            role = self._reasoner.lookup_binding_role(binding)
            concept = role.player()
        fqn = self._fqn_identifies(concept)
        return self._lookup_relation_by_fqn(fqn)

    @staticmethod
    def _fqn_identifies(concept: 'Type'):
        if isinstance(concept, EntityType):
            concept = cast(EntityType, concept)
            ref_schema_nm = concept.ref_schema_name()
        else:
            ref_schema_nm = 'identifies'
        return f'{camel_to_snake(concept.display())}__{ref_schema_nm}'

    def _transpose(self, relation: 'Relation', fqn: str):
        if fqn in self._relations:
            return self._relations[fqn]
        if relation.arity() != 2:
            raise Exception('Transposition only supported for binary relations')
        (left_concept, right_concept) = relation.signature().types()
        rel = self._model.external_relation(fqn, right_concept, left_concept)
        with rel:
            @rule()
            def transpose(left, right):
                relation(right, left)
        self._relations[fqn] = rel
        return rel

    def _gen_entity_map(self, binding: 'Binding'):
        vt_role = self._reasoner.lookup_binding_role(binding)
        et_role = vt_role.sibling()
        assert et_role is not None
        value_concept = vt_role.player()
        entity_concept = et_role.player()
        assert isinstance(entity_concept, EntityType)
        rel_nm = self._fqn_entity_map_indexed(binding, et_role)
        rel = EntityMap(Namespace.top, rel_nm, RowId, binding.column.relation(), et_role)
        role_map = self._ref_value_map(binding) \
            if isinstance(value_concept, AbstractValueType) \
            else self._ref_constructor_entity_map(binding)
        with rel:
            @rule()
            def entity_map(row, et):
                val = Vars(value_concept)
                role_map(row, val)
                if binding.column.references:
                    self._ref_identifies(binding)(val, et)
                else:
                    _ = entity_concept ^ (val, et)  # `_=` is not strictly needed, but it makes IDEs happy ;)
        self._register_relation(rel_nm, rel, self._entity_map_relations)
        self._constructor_binding_to_value_map[binding] = rel

    def _ref_constructor_entity_map(self, binding: 'Binding'):
        role = self._reasoner.lookup_binding_role(binding)
        return self._ref_entity_map(binding, role.sibling())

    def _fqn_entity_map_indexed(self, binding: 'Binding', role: Optional['Role'] = None):
        if isinstance(binding, FilteringSubtypeBinding):
            if role is None:
                bindings_list = self._reasoner.subtype_bindings_of(binding.sub_type)
                fqn = self._fqn_entity_map(binding, binding.sub_type)
                idx = bindings_list.index(binding)
            else:
                bindings_list = self._reasoner.role_bindings_of(role)
                player = role.player()
                ctor_binding = None
                # Note: this works just for one ID binding per subtype for now
                for cand_binding in bindings_list:
                    if cand_binding.column.table == binding.column.table:
                        ctor_binding = cand_binding
                        break
                assert ctor_binding is not None
                fqn = self._fqn_entity_map(binding, player)
                idx = bindings_list.index(ctor_binding)
        elif isinstance(binding, SubtypeBinding) and role is None:
            # for now, only one ref table is supported
            fqn = self._fqn_entity_map(binding, binding.sub_type)
            idx = 0
        elif role is not None:
            bindings_list = self._reasoner.role_bindings_of(role)
            fqn = self._fqn_entity_map(binding, role.player())
            idx = bindings_list.index(binding)
        else:
            raise Exception('Role can not be optional for a binding other than FilteringSubtypeBinding')
        fqn = f'{fqn}{idx}' if idx > 0 else fqn
        return fqn

    def _ref_entity_map(self, binding: 'Binding', role: 'Role') -> EntityMap:
        fqn = self._fqn_entity_map_indexed(binding, role)
        emap = self._lookup_relation_by_fqn(fqn)
        if isinstance(emap, EntityMap):
            return emap
        else:
            raise Exception(f'Relation with fully qualified name {fqn} is not an EntityMap')

    def _ref_subtype_entity_map(self, binding: 'SubtypeBinding'):
        fqn = self._fqn_entity_map(binding, binding.sub_type)
        return self._lookup_relation_by_fqn(fqn)

    @staticmethod
    def _fqn_entity_map(binding: 'Binding', concept: 'EntityType'):
        assert isinstance(concept, EntityType)
        concept_nm = camel_to_snake(concept.display())
        source_nm = binding.column.table.physical_name()
        return f'{concept_nm}__impl__{source_nm}_row_to_{concept_nm}'

    def _gen_subtype_entity_map(self, binding: 'SubtypeBinding'):
        subtype = binding.sub_type
        rel_nm = self._fqn_entity_map_indexed(binding)
        rel = EntitySubtypeMap(Namespace.top, rel_nm, RowId, binding)
        if isinstance(binding, FilteringSubtypeBinding):
            self._gen_filtering_subtype_entity_map_rule(binding, rel)
        else:
            self._gen_subtype_entity_map_rule(binding, rel)
        self._register_relation(rel_nm, rel, self._subtype_entity_map_relations)
        if subtype not in self._subtype_to_entity_map:
            self._subtype_to_entity_map[subtype] = []
        self._subtype_to_entity_map[subtype].append(rel)

    def _gen_subtype_entity_map_rule(self, binding: 'SubtypeBinding', rel: 'EntitySubtypeMap'):
        with rel:
            @rule()
            def subtype_entity_map(row, et):
                self._ref_constructor_entity_map(binding)(row, et)

    def _gen_filtering_subtype_entity_map_rule(self, binding: 'FilteringSubtypeBinding', rel: 'EntitySubtypeMap'):
        ref_ctor_emap = self._ref_constructor_entity_map(binding)
        filter_column = binding.column
        filter_value = binding.has_value
        raw_value_type = filter_column.relation().attr().type()
        if isinstance(filter_value, EntityInstanceRelation):
            filter_type = filter_value.first()
            with rel:
                @rule()
                def filtering_subtype_entity_map(row, et):
                    fv, f = Vars(filter_type, raw_value_type)
                    ref_ctor_emap(row, et)
                    filter_column(row, fv)
                    _= filter_type^(fv, f)
                    filter_value(f)
        else:
            with rel:
                @rule()
                def filtering_subtype_entity_map(row, et):
                    fv = Vars(raw_value_type)
                    ref_ctor_emap(row, et)
                    filter_column(row, fv)
                    _= fv == filter_value

    def _gen_value_map(self, binding: 'Binding'):
        role = self._reasoner.lookup_binding_role(binding)
        rel_nm = self._fqn_value_map_indexed(binding)
        rel = ValueMap(Namespace.top, rel_nm, RowId, binding.column.relation(), role)
        converter = self._value_converter(binding.column)
        with rel:
            @rule(Annotation.INLINE)
            def value_map(row, val):
                if converter:
                    orig = Vars(binding.column.type())
                    rel.attr_view()(row, orig)
                    converter(orig, val)
                else:
                    rel.attr_view()(row, val)
        self._binding_to_value_map[binding] = rel
        self._register_relation(rel_nm, rel, self._value_map_relations)

    def _fqn_value_map(self, binding: 'Binding'):
        role = self._reasoner.lookup_binding_role(binding)
        concept = role.player()
        assert isinstance(concept, AbstractValueType)
        concept_nm = camel_to_snake(concept.display())
        source_nm = binding.column.table.physical_name()
        return f'{concept_nm}__impl__{source_nm}_row_to_{concept_nm}'

    def _fqn_value_map_indexed(self, binding: 'Binding'):
        role = self._reasoner.lookup_binding_role(binding)
        role_bindings = self._reasoner.role_bindings_of(role)
        idx = role_bindings.index(binding)
        fqn = self._fqn_value_map(binding)
        fqn = f'{fqn}{idx}' if idx > 0 else fqn
        return fqn

    def _ref_value_map(self, binding: 'Binding'):
        fqn = self._fqn_value_map_indexed(binding)
        return self._lookup_relation_by_fqn(fqn)

    def _gen_entity_population(self, entity_type: 'EntityType', lookup_rel: 'AbstractRelation'):
        rel_nm = self._fqn_entity_population(entity_type)
        rel = entity_type  # in the context, an entity type can be used as the population relation
        if lookup_rel in self._preferred_id_relations:
            val_type = self._get_last_type(lookup_rel)
            with rel:
                @rule()
                def entity_population(et):
                    row = Vars(val_type)
                    lookup_rel(et, row)
        elif lookup_rel in self._subtype_entity_map_relations or isinstance(lookup_rel, CompositeEntityMap):
            with rel:
                @rule()
                def entity_population(et):
                    row = Vars(RowId)
                    lookup_rel(row, et)
        else:
            raise Exception(f'Unsupported weaving type for relation `{lookup_rel.qualified_name()}`')
        self._register_relation(rel_nm, rel, self._entity_population_relations)

    @staticmethod
    def _fqn_entity_population(entity_type: 'EntityType'):
        # entity population name is the same as the entity type name, with the first letter uppercased
        return entity_type.display()

    def _lookup_relation_by_fqn(self, fqn: str):
        if fqn in self._relations:
            return self._relations[fqn]
        else:
            raise Exception(f'Relation with fully qualified name {fqn} not found in the model')

    def _gen_semantic_predicate(self, rel_meta: 'PotentiallyBoundRelationship'):
        relationship = rel_meta.relationship
        roles = relationship.roles()
        # Each role should either be covered by a value map (AbstractValueType role) or by an entity map
        # (EntityType role), which either can be inferred if unique exists for the EntityType or must be
        # generated by the respective EntityBinding.
        role_to_role_map = {}
        for role in roles:
            role_is_bound = role in self._reasoner.role_bindings()
            player = role.player()
            # for ValueTypes we just look up ValueMap relations
            if isinstance(player, AbstractValueType):
                if not role_is_bound:
                    raise Exception(f'ValueType role {role.name()} is not bound')
                else:
                    value_maps = [self._ref_value_map(binding) for binding in self._reasoner.role_bindings()[role]]
                    if len(value_maps) == 0:
                        raise Exception(f'ValueType role {role.name()} is not correctly bound')
                    if role not in role_to_role_map:
                        role_to_role_map[role] = OrderedSet()
                    role_to_role_map[role].update(value_maps)
            elif isinstance(player, EntityType):
                entity_maps = OrderedSet()
                if not role_is_bound:
                    maps = self._lookup_inferred_entity_maps(rel_meta.table, role)
                    entity_maps.update(maps)
                else:
                    bindings = self._reasoner.role_bindings()[role]
                    for binding in bindings:
                        if isinstance(binding, RoleBinding) and binding in self._reasoner.referent_bindings():
                            binding = self._reasoner.get_ctor_binding(binding)
                        entity_map = self._ref_constructor_entity_map(binding)
                        assert entity_map is not None
                        entity_maps.add(entity_map)
                if len(entity_maps) == 0:
                    raise Exception(f'EntityType role {role.name()} is not correctly bound')
                if role not in role_to_role_map:
                    role_to_role_map[role] = OrderedSet()
                role_to_role_map[role].update(entity_maps)
            else:
                raise Exception(f'Role {role.name()} is not bound to a ValueType or EntityType')
        # if we got all roles with role maps, we can generate the rule
        items = role_to_role_map.items()
        if len(items) != relationship.arity():
            raise Exception(f'Not all roles of relationship {relationship.pprint()} are bound')
        for reading in relationship.readings():
            concept = reading.roles[0].player()
            rel_nm = reading.rel_name
            relation = concept[rel_nm]

            role_map_combinations = self._permute_role_maps(role_to_role_map, as_in=reading)
            for role_maps in role_map_combinations:
                with relation:
                    @rule()
                    def semantic_predicate(*args):
                        row = Vars(RowId)
                        for role_map, arg in zip(role_maps, args):
                            role_map(row, arg)

    def _lookup_inferred_entity_maps(self, table, role):
        player = role.player()
        unbound_error_msg = f'EntityType({player.display()}) role {role.name()} is not bound'

        if player.is_composite():
            emaps = self._composite_entity_to_entity_maps.get(player)
            if emaps is None:
                raise Exception(unbound_error_msg)
            return emaps
        ref_scheme_concept = self._reasoner.get_ref_scheme_type(player)
        if ref_scheme_concept is not None:
            if player in self._subtype_to_entity_map:
                maps = self._subtype_to_entity_map[player]
            else:
                binding = self._reasoner.lookup_ref_binding(player, table)
                if binding is None:
                    raise Exception(unbound_error_msg)
                maps = [self._ref_subtype_entity_map(binding)]
            return maps
        else:
            binding = self._reasoner.lookup_ctor_binding(player, table)
            if binding is None:
                raise Exception(unbound_error_msg)
            return [self._ref_constructor_entity_map(binding)]

    @staticmethod
    def _permute_role_maps(role_to_role_map: dict['Role', OrderedSet['RoleMap']], as_in: 'Reading'):
        try:
            role_map_combinations = product(*(role_to_role_map[role] for role in as_in.roles))
            return [list(combination) for combination in role_map_combinations]
        except KeyError as e:
            missing_role = e.args[0]
            raise Exception(f'Cannot permute role maps to match reading `{as_in.rel_name}`, role `{missing_role.name()}` not found')

    @staticmethod
    def _get_last_type(lookup_rel: 'AbstractRelation'):
        return lookup_rel.signature().types()[-1]

    def _register_relation(self, name: str, rel: Union[AbstractRelation, EntityType],
                           population: OrderedSet['AbstractRelation'] = None):
        if isinstance(rel, RoleMap) or isinstance(rel, EntitySubtypeMap) or isinstance(rel, CompositeEntityMap):
            self._model._add_relation(rel)
        self._relations[name] = rel
        if population is not None:
            population.add(rel)

    def _cfg_decimal_size(self):
        return self._config['decimal_size']

    def _cfg_decimal_scale(self):
        return self._config['decimal_scale']
