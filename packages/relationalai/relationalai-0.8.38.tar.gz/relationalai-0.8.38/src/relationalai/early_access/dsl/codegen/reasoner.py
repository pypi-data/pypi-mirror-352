# pyright: reportArgumentType=false
from typing import cast, Union

from relationalai.early_access.dsl.bindings.tables import (FilteringSubtypeBinding, ConceptBinding, IdentifierBinding,
                                                           SubtypeBinding, RoleBinding, Binding, ColumnRef,
                                                           SnowflakeTable)
from relationalai.early_access.dsl.codegen.common import PotentiallyBoundRelationship, BoundExternalPreferredUC
from relationalai.early_access.dsl.core.types import AbstractValueType
from relationalai.early_access.dsl.core.types import Type
from relationalai.early_access.dsl.ontologies.constraints import Unique, Mandatory
from relationalai.early_access.dsl.ontologies.relationships import Relationship
from relationalai.early_access.dsl.ontologies.roles import Role, AbstractRole
from relationalai.early_access.dsl.types.entities import EntityType
from relationalai.early_access.metamodel.util import OrderedSet


class Reasoner:
    def __init__(self, model):
        self._model = model

        # Maps for type relationships
        self._subtype_map: dict['EntityType', OrderedSet['EntityType']] = {}
        self._supertype_map: dict['EntityType', OrderedSet['EntityType']] = {}
        self._subtype_closure: dict[Type, OrderedSet[Type]] = {}
        self._supertype_closure: dict[Type, OrderedSet[Type]] = {}
        self._type_closure: dict[Type, OrderedSet[Type]] = {}

        # Bindings
        self._value_type_bindings: OrderedSet[Binding] = OrderedSet()
        self._entity_type_bindings: OrderedSet[Binding] = OrderedSet()
        self._constructor_bindings: OrderedSet[Union[IdentifierBinding, SubtypeBinding]] = OrderedSet()
        self._filtering_bindings: OrderedSet[FilteringSubtypeBinding] = OrderedSet()
        self._referent_constructor_bindings: OrderedSet[Union[IdentifierBinding, SubtypeBinding]] = OrderedSet()
        self._referent_bindings: OrderedSet[RoleBinding] = OrderedSet()
        self._subtype_bindings: OrderedSet[SubtypeBinding] = OrderedSet()
        self._subtype_binding_references: dict[SubtypeBinding, Role] = {}
        self._constructor_binding_binds_to: dict[IdentifierBinding, Role] = {}
        self._role_bound_thru: dict[Role, list[Binding]] = {}
        self._subtype_bound_thru: dict[EntityType, list[Binding]] = {}
        self._ref_binding_to_ctor_binding: dict[Binding, Binding] = {}
        self._concept_binding_to_actual: dict[Binding, Binding] = {}

        # Relationships & Ontological Constraints
        self._unary_relationships: OrderedSet['Relationship'] = OrderedSet()
        self._binary_relationships: OrderedSet['Relationship'] = OrderedSet()
        self._identifier_relationships: OrderedSet['Relationship'] = OrderedSet()
        self._entity_identifier_relationships: OrderedSet['Relationship'] = OrderedSet()
        self._entity_type_identifier: dict['EntityType', 'Relationship'] = {}
        self._bound_relationships: OrderedSet['PotentiallyBoundRelationship'] = OrderedSet()
        self._bound_external_ucs: OrderedSet['BoundExternalPreferredUC'] = OrderedSet()
        self._internal_preferred_uc: OrderedSet['Unique'] = OrderedSet()
        self._external_preferred_uc: OrderedSet['Unique'] = OrderedSet()
        self._constructor_roles: OrderedSet['AbstractRole'] = OrderedSet()
        self._internal_uc_roles: OrderedSet['Role'] = OrderedSet()
        self._mandatory_roles: OrderedSet['Role'] = OrderedSet()
        self._bound_role: dict['Role', list['Binding']] = {}
        self._ref_type_of: dict['EntityType', 'EntityType'] = {}
        self._inclusive_entity_types: OrderedSet['EntityType'] = OrderedSet()
        self._composite_entity_types: OrderedSet['EntityType'] = OrderedSet()
        self._identifiers_of_subtype: dict[EntityType, OrderedSet[Union['Relationship', 'Unique']]] = {}

        self._col_ref_to_pid_concept: dict['ColumnRef', 'EntityType'] = {}

    def subtype_map(self):
        return self._subtype_map

    def value_type_bindings(self):
        return self._value_type_bindings

    def constructor_bindings(self):
        return self._constructor_bindings

    def referent_constructor_bindings(self):
        return self._referent_constructor_bindings

    def subtype_bindings(self):
        return self._subtype_bindings

    def subtype_bindings_of(self, subtype: Type):
        assert isinstance(subtype, EntityType)
        return self._subtype_bound_thru[subtype]

    def bound_relationships(self):
        return self._bound_relationships

    def bound_external_ucs(self):
        return self._bound_external_ucs

    def referent_bindings(self):
        return self._referent_bindings

    def role_bindings(self):
        return self._bound_role

    def role_bindings_of(self, role: Role):
        return self._role_bound_thru[role]

    def get_ref_scheme_type(self, entity_type: Type):
        assert isinstance(entity_type, EntityType)
        return self._ref_type_of.get(entity_type)

    def get_ctor_binding(self, ref_binding: Binding):
        return self._ref_binding_to_ctor_binding[ref_binding]

    def referenced_concept(self, col_ref: ColumnRef):
        return self._col_ref_to_pid_concept.get(col_ref)

    def analyze(self):
        self._analyze_constraints()
        self._analyze_subtypes()
        potentially_bound_rels = self._analyze_bindings()
        self._analyze_ctor_roles()
        self._analyze_relationships()
        self._analyze_bound_external_ucs()
        self._analyze_bound_relationships(potentially_bound_rels)

        self._process_bound_relationships()
        self._process_referent_bindings()

    def _analyze_subtypes(self):
        # Initialize subtype and supertype maps
        for subtype_arrow in self._model._subtype_arrows:
            parent = subtype_arrow.end
            child = subtype_arrow.start
            self._subtype_map.setdefault(parent, OrderedSet()).add(child)
            self._supertype_map.setdefault(child, OrderedSet()).add(parent)

        self._analyze_subtype_identifiers()

        # Compute closures for subtypes, supertypes, and types
        self._subtype_closure = {}
        self._supertype_closure = {}
        self._type_closure = {}

        for entity in self._subtype_map.keys() | self._supertype_map.keys():
            self._subtype_closure[entity] = self._compute_closure(entity, self._subtype_map)
            self._supertype_closure[entity] = self._compute_closure(entity, self._supertype_map)
            self._type_closure[entity] = self._subtype_closure[entity] | self._supertype_closure[entity]

    def _analyze_subtype_identifiers(self):
        # Find all leaf subtypes
        leaf_types = OrderedSet()
        non_leaf_types = OrderedSet()
        non_leaf_types.update(self._subtype_map.keys())

        for entity in self._supertype_map:
            if entity in self._subtype_map:
                non_leaf_types.add(entity)
            else:
                leaf_types.add(entity)

        # If leaf has an ID relationship then that's what we use or else look up it bottom up and throw if none found
        memo = set()
        for leaf_type in leaf_types:
            self._find_supertype_identifier_bottom_up(leaf_type, memo, [])

        # For any intermediate or root nodes that didn't get an ID relationship during the bottom-up, try that followed
        # by a top-down lookup (may result in multiple ID relationships from different subtypes)
        for non_leaf_type in non_leaf_types:
            if non_leaf_type in memo:
                continue
            try:
                self._find_supertype_identifier_bottom_up(non_leaf_type, memo, [])
            except KeyError:
                # ignore error, since the top-down approach will throw if none exists either
                self._find_subtype_identifiers_top_down(non_leaf_type, memo, [])

    def _find_supertype_identifier_bottom_up(self, entity_type: EntityType, memo: set[EntityType],
                                             lookup_chain: list[str]):
        """
        Looks up an Identifier relationship or a preferred External UC for an entity type bottom up or throws an error
        otherwise.

        It's designed to be used on leaf types. If used on intermediate nodes if they don't have a preferred ID, any
        exception should be swallowed and top-down used to look up a set of possible ID relationships coming from its
        subtypes.
        """
        if entity_type in memo:
            return self._identifiers_of_subtype.get(entity_type)

        if lookup_chain is None:
            lookup_chain = []
        lookup_chain.append(entity_type.display())

        identifier = self._model.identifier_of(entity_type)
        if identifier is not None:
            ids = OrderedSet()
            ids.add(identifier)
            self._identifiers_of_subtype[entity_type] = ids
            memo.add(entity_type)  # use memoization to reduce lookups
            return ids
        # Check supertype
        supertypes = self._supertype_map.get(entity_type)
        if supertypes is None:
            raise KeyError(f'No reference scheme found for {entity_type}, in chain {lookup_chain}')
        if len(supertypes) > 1:
            raise NotImplementedError(f'Multiple supertypes are not supported yet (in {entity_type})')
        for supertype in supertypes:
            ids = self._find_supertype_identifier_bottom_up(supertype, memo, lookup_chain)
            self._identifiers_of_subtype[entity_type] = ids
            memo.add(entity_type)  # use memoization to reduce lookups
            return ids

    def _find_subtype_identifiers_top_down(self, entity_type: EntityType, memo: set[EntityType],
                                           lookup_chain: list[str]):
        if entity_type in memo:
            return self._identifiers_of_subtype.get(entity_type)

        subtypes = self._subtype_map.get(entity_type)
        if subtypes is None:
            raise KeyError(f'No reference scheme found for {entity_type}, in chain {lookup_chain}')

        ids = OrderedSet()
        for subtype in subtypes:
            identifier = self._model.identifier_of(subtype)
            if identifier is not None:
                ids.add(identifier)
            else:
                subtype_ids = self._find_subtype_identifiers_top_down(subtype, memo, lookup_chain)
                ids.update(subtype_ids)

        self._identifiers_of_subtype[entity_type] = ids
        memo.add(entity_type)  # use memoization to reduce lookups
        return ids

    @staticmethod
    def _compute_closure(entity, relation_map):
        closure = OrderedSet()
        stack = [entity]
        while stack:
            current = stack.pop()
            for related in relation_map.get(current, []):
                if related not in closure:
                    closure.add(related)
                    stack.append(related)
        return closure

    def _analyze_bindings(self):
        potentially_bound_rels = {}
        for binding in self._model._bindings:
            role = self._process_binding(binding)
            # if role is None then such binding doesn't bind to a role
            if role is None:
                continue

            if isinstance(binding, ConceptBinding):
                binding = self._concept_binding_to_actual[binding]

            if role not in self._bound_role:
                self._bound_role[role] = []
            self._bound_role[role].append(binding)
            self._categorize_binding(binding, role)

            # Group bindings by relationship and table
            rel = PotentiallyBoundRelationship(role.part_of, binding.column.table)
            if rel not in potentially_bound_rels:
                potentially_bound_rels[rel] = []
            potentially_bound_rels[rel].append(binding)
        return potentially_bound_rels

    def _process_binding(self, binding: 'Binding'):
        """Dispatch binding to the appropriate type-specific handler."""
        if isinstance(binding, ConceptBinding):
            role = self._handle_concept_binding(binding)
        elif isinstance(binding, FilteringSubtypeBinding):
            return self._handle_filtering_binding(binding)
        elif isinstance(binding, SubtypeBinding):
            role = self._handle_subtype_binding(binding)
        elif isinstance(binding, IdentifierBinding):
            role = self._handle_identifier_binding(binding)
        elif isinstance(binding, RoleBinding):
            role = self._handle_role_binding(binding)
        else:
            raise Exception(f'{binding} is yet not supported')

        if role is None:
            raise Exception(f'Unable to lookup binding role for {binding}')
        return role

    def _handle_concept_binding(self, binding: 'ConceptBinding'):
        entity_type = binding.entity_type
        if entity_type in self._inclusive_entity_types:
            actual_binding = IdentifierBinding(binding.column, entity_type=entity_type)
        else:
            actual_binding = SubtypeBinding(binding.column, sub_type=entity_type)
        # Store the actual binding for later reference
        self._concept_binding_to_actual[binding] = actual_binding
        return self._process_binding(actual_binding)

    def _handle_filtering_binding(self, binding: 'FilteringSubtypeBinding'):
        """Process FilteringSubtypeBinding and update filtering and subtype sets."""
        binding = cast(FilteringSubtypeBinding, binding)
        self._filtering_bindings.add(binding)
        self._subtype_bindings.add(binding)
        sub_type = binding.sub_type
        self._ref_type_of[sub_type] = sub_type
        # Initialize list if subtype is encountered for the first time
        if sub_type not in self._subtype_bound_thru:
            self._subtype_bound_thru[sub_type] = []
        self._subtype_bound_thru[sub_type].append(binding)
        return None  # Explicitly return None for filtering bindings

    def _handle_subtype_binding(self, binding: 'SubtypeBinding'):
        """Process SubtypeBinding by looking up ref type and role."""
        ref_types = self._lookup_ref_types_of(binding.sub_type)
        if len(ref_types) > 1:
            raise Exception(f'Multiple ref types are not yet supported, (type: {binding.sub_type})')
        ref_type = ref_types[0]
        role = self._lookup_ctor_role(ref_type)
        self._subtype_binding_references[binding] = role
        self._subtype_bindings.add(binding)
        self._ref_type_of[binding.sub_type] = ref_type
        return role

    def _handle_identifier_binding(self, binding: 'IdentifierBinding'):
        """Process IdentifierBinding by looking up its constructor role."""
        role = self._lookup_ctor_role(binding.entity_type)
        self._constructor_binding_binds_to[binding] = role
        return role

    @staticmethod
    def _handle_role_binding(binding: 'RoleBinding'):
        """Process RoleBinding by directly using the role attribute."""
        return binding.role

    def _lookup_identifiers_of(self, entity_type: EntityType):
        identifier = self._model.identifier_of(entity_type)
        if identifier is not None:
            ids = OrderedSet()
            ids.add(identifier)
            return ids
        ids = self._identifiers_of_subtype.get(entity_type)
        if ids is not None:
            return ids
        raise Exception(f'Cannot look up identifier relationship for {entity_type.display()}')

    def _lookup_ref_types_of(self, entity_type: EntityType):
        ids = self._lookup_identifiers_of(entity_type)
        ref_types = OrderedSet()
        for identifier in ids:
            for role in self._get_identifier_roles(identifier):
                if role in self._constructor_roles:
                    sibling_role = role.sibling()
                    assert sibling_role is not None
                    ref_types.add(sibling_role.player())
                    break
        return ref_types

    @staticmethod
    def _get_identifier_roles(identifier):
        if isinstance(identifier, Relationship) or isinstance(identifier, Unique):
            return identifier.roles()
        else:
            raise ValueError(f'Identifier type {type(identifier)} is not supported')

    def _lookup_ctor_role(self, entity_type: 'EntityType'):
        ids = self._lookup_identifiers_of(entity_type)
        if len(ids) > 1:
            raise NotImplementedError(f'Multiple identifier lookups are not yet supported (type: {entity_type.display()})')

        identifier = ids[0]
        for role in self._get_identifier_roles(identifier):
            player = role.player()
            if player == entity_type or self._is_part_of_type_closure(entity_type, player):
                # ctor role is the only sibling of the constructed entity type role
                return role.sibling()
        raise ValueError(f'Cannot find ctor role for {entity_type}')

    def _is_part_of_type_closure(self, entity_type: EntityType, other: Type):
        closure = self._type_closure.get(entity_type)
        return closure is not None and other in closure

    def _categorize_binding(self, binding: 'Binding', role: 'Role'):
        player = role.player()
        if isinstance(player, AbstractValueType):
            self._value_type_bindings.add(binding)
        elif isinstance(player, EntityType):
            self._entity_type_bindings.add(binding)
        else:
            raise Exception(f'Binding {binding} is not supported')

    def _analyze_constraints(self):
        for constraint in self._model.constraints():
            if isinstance(constraint, Unique):
                self._process_uc(constraint)
            elif isinstance(constraint, Mandatory):
                self._mandatory_roles.update(constraint.roles())

    def _process_uc(self, constraint: 'Unique'):
        if not constraint.is_preferred_identifier:
            return

        roles = constraint.roles()
        self._constructor_roles.update(roles)  # Mark as constructor roles

        num_roles = len(roles)
        if num_roles == 1:
            self._process_internal_uc(constraint)
        elif num_roles > 1:
            self._external_preferred_uc.add(constraint)

    def _process_internal_uc(self, constraint: Unique):
        self._internal_preferred_uc.add(constraint)

        roles = constraint.roles()
        constructor_role = roles[0]
        rel = constructor_role.part_of

        if rel.arity() != 2:
            raise Exception('Invalid Identifier relationship configuration')

        player = constructor_role.player()
        if isinstance(player, AbstractValueType):
            self._identifier_relationships.add(rel)
        elif isinstance(player, EntityType):
            self._entity_identifier_relationships.add(rel)
        else:
            raise Exception(f'Identifier relationship {rel.pprint()} has unsupported player type {player.name()}')

        concept = constructor_role.sibling().player()
        self._entity_type_identifier[concept] = rel
        self._inclusive_entity_types.add(concept)

    def _analyze_ctor_roles(self):
        for constructor_role in self._constructor_roles:
            self._classify_constructor_bindings(constructor_role)

    def _classify_constructor_bindings(self, constructor_role: 'Role'):
        if constructor_role not in self._bound_role:
            return

        for binding in self._bound_role[constructor_role]:
            if isinstance(binding, IdentifierBinding):
                if not binding.column.references:
                    role = self.lookup_binding_role(binding)
                    self._col_ref_to_pid_concept[binding.column.ref()] = role.player()
                    self._constructor_bindings.add(binding)
                else:
                    self._referent_constructor_bindings.add(binding)
            elif isinstance(binding, SubtypeBinding):
                self._referent_constructor_bindings.add(binding)

    def _analyze_relationships(self):
        for relationship in self._model.relationships():
            arity = relationship.arity()
            if arity == 1:
                self._unary_relationships.add(relationship)
            elif arity == 2:
                self._binary_relationships.add(relationship)

    def _analyze_bound_relationships(self, potentially_bound_rels):
        for rel, bindings in potentially_bound_rels.items():
            rel.bindings.extend(bindings)
            self._analyze_bound_relationship(rel)

    def _analyze_bound_relationship(self, meta: 'PotentiallyBoundRelationship'):
        arity = meta.relationship.arity()
        if arity == 1:
            # Handle unary relationships
            if meta.bindings:
                self._bound_relationships.add(meta)
            return
        elif arity == 2:
            self._process_binary_bound_relationship(meta)
        else:
            self._process_nary_bound_relationship(meta)

    def _process_binary_bound_relationship(self, meta: PotentiallyBoundRelationship):
        relationship = meta.relationship
        key_role, value_role = self._identify_roles(relationship)
        key_type, value_type = key_role.player(), value_role.player()
        if not isinstance(key_type, EntityType):
            raise Exception(f'Key role played by {key_type.display()} must be an entity type')
        # TODO : this below should really check if they bound for the same table
        key_role_is_bound = key_role in self._bound_role
        value_role_is_bound = value_role in self._bound_role
        value_role_is_ctor = value_role in self._constructor_roles
        key_role_infers_emap = self._infers_key_role_emap(key_type, meta.table, key_role_is_bound, value_role_is_ctor)
        fully_bound = value_role_is_bound and (key_role_is_bound or key_role_infers_emap)
        is_bound_value_type_relationship = isinstance(value_type, AbstractValueType) and fully_bound
        is_bound = self._is_bound_identifier_relationship(value_role_is_ctor, value_role_is_bound, key_role_is_bound) or \
                   is_bound_value_type_relationship or \
                   self._is_bound_entity_type_relationship(key_type, value_type, key_role, value_role, meta.table)
        if is_bound:
            self._bound_relationships.add(meta)
        else:
            raise Exception(
                f'Bound relationship `{relationship.pprint()}` must have at least one bound role and '
                f'one inferred entity map'
            )

    def _process_nary_bound_relationship(self, meta: PotentiallyBoundRelationship):
        relationship = meta.relationship
        roles = relationship.roles()
        has_entity_type_player = False
        bound_roles = OrderedSet()
        for binding in meta.bindings:
            if not isinstance(binding, RoleBinding):
                raise Exception(f'Every binding in an N-ary relationship must be a RoleBinding, {relationship.pprint()}')
            bound_roles.add(binding.role)
        is_bound = True
        for role in roles:
            if isinstance(role.player(), EntityType):
                has_entity_type_player = True
            if role not in bound_roles:
                is_bound = False
                break
        if not has_entity_type_player:
            raise ValueError(
                f'Bound relationship `{relationship.pprint()}` must have at least one Role played by an entity type'
            )
        if is_bound:
            self._bound_relationships.add(meta)
        else:
            raise Exception(f'Bound relationship `{relationship.pprint()}` must have all roles bound')

    def _identify_roles(self, rel: 'Relationship') -> tuple['Role', 'Role']:
        key_role, value_role = None, None
        for role in rel.roles():
            if isinstance(role.player(), AbstractValueType):
                value_role = role
            # if both roles are entity types, arbitrarily pick one as the key role
            elif key_role is None and role not in self._constructor_roles:
                key_role = role
            else:
                value_role = role
        assert key_role is not None
        assert value_role is not None
        return key_role, value_role

    def _infers_key_role_emap(self, key_type: EntityType, table, key_role_is_bound, value_role_is_ctor):
        if key_role_is_bound or value_role_is_ctor:
            return False
        if key_type.is_composite():
            return self._exists_bound_external_uc(key_type, table)
        return self._exists_ctor_binding(key_type, table) or self._exists_ref_binding(key_type, table) or\
                self._exists_subtype_binding(key_type, table)

    def _exists_bound_external_uc(self, key_type, table):
        for bound_constraint in self._bound_external_ucs:
            if bound_constraint.concept == key_type and bound_constraint.table == table:
                return True
        return False

    def _exists_subtype_binding(self, entity_type, table):
        if entity_type not in self._supertype_map:
            return False

        for binding in self._subtype_bindings:
            if binding.column.table == table and binding.sub_type == entity_type:
                ref_types = self._lookup_ref_types_of(entity_type)
                # TODO: check how this works with multi-table inheritance
                for ref_type in ref_types:
                    if self._exists_ctor_binding(ref_type, table):
                        return True
        return False

    @staticmethod
    def _is_bound_identifier_relationship(value_role_is_ctor, value_role_is_bound, key_role_is_bound):
        if value_role_is_ctor and value_role_is_bound:
            if key_role_is_bound:
                raise Exception('Identifier relationship must not have the key role bound')
            return True
        return False

    def _is_bound_entity_type_relationship(self, key_type, value_type, key_role, value_role, table):
        if isinstance(value_type, EntityType) and isinstance(key_type, EntityType):
            value_role_infers_emap = self._exists_ctor_binding(value_type, table) or self._exists_ref_binding(value_type, table)
            return (
                (key_role in self._bound_role and value_role in self._bound_role) or
                (value_role in self._bound_role and value_role_infers_emap) or
                (key_role in self._bound_role and value_role_infers_emap)
            )
        if isinstance(value_type, AbstractValueType) and isinstance(key_type, AbstractValueType):
            raise Exception('Binary Relationship cannot have more than one ValueType role')
        return False

    def _exists_ctor_binding(self, entity_type: 'EntityType', table: 'SnowflakeTable'):
        return self.lookup_ctor_binding(entity_type, table) is not None

    def lookup_ctor_binding(self, entity_type: 'EntityType', table: 'SnowflakeTable'):
        # TODO : implement more efficient lookup
        for binding, role in self._constructor_binding_binds_to.items():
            sibling_role = role.sibling()
            assert sibling_role is not None
            if sibling_role.player() == entity_type and binding.column.table == table:
                return binding
        if entity_type in self._subtype_closure:
            for subtype in self._subtype_closure[entity_type]:
                cand = self.lookup_ctor_binding(subtype, table)
                if cand:
                    return cand
        return None

    def _exists_ref_binding(self, entity_type: 'EntityType', table: 'SnowflakeTable'):
        return self.lookup_ref_binding(entity_type, table) is not None

    def lookup_ref_binding(self, entity_type: 'EntityType', table: 'SnowflakeTable'):
        # TODO : implement more efficient lookup
        for binding, role in self._subtype_binding_references.items():
            if isinstance(binding, SubtypeBinding):
                binding = cast(SubtypeBinding, binding)
                sibling_role = role.sibling()
                assert sibling_role is not None
                ref_type = self._ref_type_of[binding.sub_type]
                if sibling_role.player() == ref_type and binding.column.table == table and entity_type == binding.sub_type:
                    return binding
        if entity_type in self._subtype_closure:
            for subtype in self._subtype_closure[entity_type]:
                cand = self.lookup_ref_binding(subtype, table)
                if cand:
                    return cand
        return None

    def lookup_binding_role(self, binding: 'Binding'):
        if isinstance(binding, IdentifierBinding):
            role = self._constructor_binding_binds_to[binding]
        elif isinstance(binding, RoleBinding):
            role = binding.role
        elif isinstance(binding, FilteringSubtypeBinding):
            role = self._lookup_ctor_role(binding.sub_type)
        elif isinstance(binding, SubtypeBinding):
            role = self._subtype_binding_references[binding]
        else:
            raise Exception(f'Binding {binding} is not supported')
        if role is None:
            raise Exception(f'Unable to lookup binding role for {binding}')
        return role

    def _process_bound_relationships(self):
        for rel_meta in self._bound_relationships:
            if self.is_identifier_relationship(rel_meta.relationship):
                self._process_identifier_relationship(rel_meta)
            else:
                self._process_non_identifier_relationship(rel_meta)

    def is_identifier_relationship(self, relationship):
        return relationship in self._identifier_relationships or \
               relationship in self._entity_identifier_relationships

    def _process_identifier_relationship(self, rel_meta):
        roles = rel_meta.relationship.roles()
        ctor_role, concept_role = self._classify_identifier_roles(roles)
        ctor_role_bindings, concept_role_bindings = self._categorize_bindings(rel_meta.bindings)
        self._update_role_bound_thru(ctor_role, ctor_role_bindings)
        self._update_role_bound_thru(concept_role, concept_role_bindings)

    def _classify_identifier_roles(self, roles):
        ctor_role = next((role for role in roles if role in self._constructor_roles), None)
        concept_role = next((role for role in roles if role != ctor_role), None)
        return ctor_role, concept_role

    def _categorize_bindings(self, bindings):
        ctor_role_bindings = []
        concept_role_bindings = []
        for binding in bindings:
            if binding in self._constructor_bindings:
                ctor_role_bindings.append(binding)
                concept_role_bindings.append(binding)
            elif binding in self._referent_constructor_bindings:
                ctor_role_bindings.append(binding)
                concept_role_bindings.append(binding)
            elif binding in self._subtype_bindings:
                concept_role_bindings.append(binding)
        return ctor_role_bindings, concept_role_bindings

    def _update_role_bound_thru(self, role, bindings):
        if role not in self._role_bound_thru:
            self._role_bound_thru[role] = []
        self._role_bound_thru[role].extend(bindings)

    def _process_non_identifier_relationship(self, rel_meta):
        role_bindings = {}
        for binding in rel_meta.bindings:
            role = self.lookup_binding_role(binding)
            role_bindings.setdefault(role, []).append(binding)
            if isinstance(binding, RoleBinding) and isinstance(binding.role.player(), EntityType):
                self._referent_bindings.add(binding)
        self._role_bound_thru.update(role_bindings)

    def _process_referent_bindings(self):
        for binding in self._referent_bindings:
            ctor_binding = self._lookup_binding_reference(binding)
            self._ref_binding_to_ctor_binding[binding] = ctor_binding

    def _lookup_binding_reference(self, binding):
        concept = binding.role.player()
        # case 1: concept is an entity type with a reference scheme - just look up the ID relationship
        if concept in self._inclusive_entity_types:
            return self._lookup_inclusive_type_binding(concept, binding)
        # case 2: concept is an entity type with a composite reference scheme
        elif concept in self._composite_entity_types:
            # TODO implement composite reference scheme
            raise Exception('Composite reference scheme not supported yet')
        # case 3: concept has no reference scheme, e.g. exclusive entity type
        else:
            # In this case we look up an IdentifierBinding that has the same column as the binding
            # and role player as the same entity type played by the binding. It must be unique,
            # otherwise we raise an exception.
            cand_bindings = []
            ref_types = self._lookup_ref_types_of(concept)
            for ref_type in ref_types:
                cand_binding = self._lookup_inclusive_type_binding(ref_type, binding)
                if cand_binding and cand_binding.column == binding.column and concept in self._type_closure[ref_type]:
                    cand_bindings.append(cand_binding)
            if len(cand_bindings) != 1:
                raise Exception(f'Binding {binding} has no unique reference to an IdentifierBinding')
            else:
                return cand_bindings[0]

    def _lookup_inclusive_type_binding(self, ref_concept: 'EntityType', binding: 'Binding'):
        identifier_relationship = self._model.identifier_of(ref_concept)
        # TODO optimize
        ctor_binding = None
        concept_role = None
        for role in identifier_relationship.roles():
            if role in self._constructor_roles:
                concept_role = role.sibling()
            else:
                concept_role = role
            break
        for cand_binding in self._role_bound_thru[concept_role]:
            if isinstance(cand_binding, IdentifierBinding) and binding.column == cand_binding.column:
                ctor_binding = cand_binding
                break
        return ctor_binding

    def _analyze_bound_external_ucs(self):
        for unique_constraint in self._external_preferred_uc:
            roles = unique_constraint.roles()
            role_bindings_by_table = self._collect_table_role_bindings(roles)
            for table, role_bindings in role_bindings_by_table.items():
                if len(role_bindings) < len(roles):
                    raise Exception(
                        f'External preferred identifier {unique_constraint} must have all roles bound'
                    )
                bound_uc = BoundExternalPreferredUC(unique_constraint, table, role_bindings)
                self._bound_external_ucs.add(bound_uc)

    def _collect_table_role_bindings(self, roles):
        role_bindings_by_table = {}
        for role in roles:
            bindings = self._bound_role.get(role)
            if not bindings:
                continue
            for binding in bindings:
                table = binding.column.table
                role_bindings_by_table.setdefault(table, {}).setdefault(role, []).append(binding)
        return role_bindings_by_table
