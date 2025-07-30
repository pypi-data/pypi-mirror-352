from __future__ import annotations

from collections import OrderedDict
from typing import Optional, Any, Sequence, Union, TypeVar

import relationalai.early_access.builder as qb
from relationalai import Config
from relationalai.early_access.dsl.bindings.tables import Binding
from relationalai.early_access.dsl.bindings.tables import SnowflakeTable, CsvTable
from relationalai.early_access.dsl.codegen.weaver import Weaver
from relationalai.early_access.dsl.core.types.unconstrained import UnconstrainedValueType
from relationalai.early_access.dsl.core.utils import generate_stable_uuid, to_pascal_case
from relationalai.early_access.dsl.orm.constraints import Unique, Mandatory, RoleValueConstraint, Range, \
    ExclusiveSubtypeConstraint, InclusiveSubtypeConstraint, InclusiveRoleConstraint, ExclusiveRoleConstraint
from relationalai.early_access.dsl.orm.relationships import Relationship, Role
from relationalai.early_access.dsl.orm.types import Concept
from relationalai.early_access.dsl.snow.api import Executor
from relationalai.early_access.metamodel.util import OrderedSet

T = TypeVar('T', int, float, str)

class Model:
    def __init__(
            self,
            name: str,
            is_primary: bool = True,
            dry_run: bool = False,
            config: Optional[Config] = None
    ):
        self.name = name
        self._qb_model = qb.Model(name, dry_run=dry_run, config=config)
        self.is_primary = is_primary
        self._constraints = OrderedSet()
        self._entity_to_id_relationship = OrderedDict()
        self._bindable_tables = OrderedDict()
        self._bindings = []
        self._executor = None
        self._weaver = Weaver(self)
        self._queries = OrderedSet()
        self.Enum = self._qb_model.Enum

    def guid(self):
        return generate_stable_uuid(self.name)

    def Concept(self, name: str, extends: list[Any] = [], identify_by:dict[str, Any]={}) -> Concept:
        name = to_pascal_case(name)
        self._validate_type_name(name)
        c = Concept(self, name, extends, identify_by)
        if name not in self.qb_model().concepts:
            self.qb_model().concepts[name] = c
        return c

    def qb_model(self):
        return self._qb_model

    def Relationship(self, reading: Any, short_name:str="") -> qb.Relationship:
        """
        Create a new relationship with the given reading.
        """
        return Relationship(self, reading, short_name=short_name)

    def constraint(self, constraint):
        # Generic constraint addition with validation
        self._constraints.add(constraint)
        constraint._desugar()

    def unique(self, *roles):
        self.constraint(Unique(*roles))

    def mandatory(self, role):
        self.constraint(Mandatory(role))

    def inclusive_roles(self, *roles):
        self.constraint(InclusiveRoleConstraint(*roles))

    def exclusive_roles(self, *roles):
        self.constraint(ExclusiveRoleConstraint(*roles))

    def role_value_constraint(self, role: Role, values: Sequence[Union[T, Range[T]]]):
        first_type = values[0]._type() if isinstance(values[0], Range) else type(values[0])
        for v in values[1:]:
            t = v._type() if isinstance(v, Range) else type(v)
            if t != first_type:
                raise Exception("Values for role value constraint must have the same type.")
        if role.player()._is_primitive() or role.player()._is_value_type():
            self.constraint(RoleValueConstraint(role, values))
        else:
            raise Exception("A role value constraint can only be applied to roles played by value types")

    def exclusive_subtype_constraint(self, *concepts:Concept):
        self.constraint(ExclusiveSubtypeConstraint(*concepts))

    def inclusive_subtype_constraint(self, *concepts:Concept):
        self.constraint(InclusiveSubtypeConstraint(*concepts))

    def _ref_scheme_constraints(self, *relations:Relationship):
        if len(relations) == 1:
            # binary case, internal UC
            role = relations[0][1]
            self._internal_preferred_uc(role)
        else:
            roles = [rel[1] for rel in relations]
            self._composite_preferred_uc(*roles)

    def _internal_preferred_uc(self, role):
        rel = role._part_of()
        if rel._arity() != 2:
            raise Exception("The relationship should be binary to apply preferred identifier constraint")
        # mark the role as preferred identifier
        self.constraint(Unique(role, is_preferred_identifier=True))
        # mark the sibling role as mandatory and unique
        sibling = role.sibling()
        self.mandatory(sibling)
        self.unique(sibling)

    def _composite_preferred_uc(self, *roles):
        for role in roles:
            sibling = role.sibling()
            if not sibling:
                raise Exception("Composite preferred identifier constraint should be applied on binary relationships")
            self.mandatory(sibling)
            self.unique(sibling)
        self.constraint(Unique(*roles, is_preferred_identifier=True))

    def lookup_concept(self, name) -> Optional[qb.Concept]:
        name = to_pascal_case(name)
        if name in self._qb_model.concepts:
            return self._qb_model.concepts[name]
        return None

    def constraints(self):
        """Getter for the _constraints property"""
        return self._constraints

    def queries(self):
        return self._queries

    def concepts(self):
        return list(self._qb_model.concepts.values())

    def concepts_map(self):
        return self._qb_model.concepts

    def value_types(self):
        return list(filter(lambda c: c._is_primitive(), self._qb_model.concepts.values()))

    def value_types_map(self):
        return dict(filter(lambda item: item[1]._is_primitive(), self._qb_model.concepts.items()))

    def entity_types(self):
        return list(filter(lambda c: not c._is_primitive(), self._qb_model.concepts.values()))

    def entity_types_map(self):
        return dict(filter(lambda item: not item[1]._is_primitive(), self._qb_model.concepts.items()))

    def relationships(self):
        return self._qb_model.relationships

    def bindable_tables(self):
        return self._bindable_tables

    def api(self):
        self._executor = self._executor or Executor(self._qb_model._config)
        return self._executor

    def table(self, name: str) -> SnowflakeTable:
        metadata = self.api().table_metadata(name)
        table = SnowflakeTable(metadata, self)
        self._bindable_tables[name] = table
        return table

    def csv_table(self, name: str, schema: dict[str, UnconstrainedValueType]) -> CsvTable:
        table = CsvTable(name, schema, self)
        self._bindable_tables[name] = table
        return table

    def binding(self, binding: Binding):
        self._bindings.append(binding)

    def generate_weaving_rules(self):
        self._weaver.generate()

    def _validate_type_name(self, name):
        if name in self._qb_model.concepts:
            raise Exception(
                f"The name '{name}' is used to declare a Concept.")
