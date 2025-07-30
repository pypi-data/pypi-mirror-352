import typing

from relationalai.early_access.dsl.graph.graph import topological_sort
from relationalai.early_access.dsl.orm.constraints import Unique, Mandatory, RoleValueConstraint, \
    InclusiveSubtypeConstraint, ExclusiveSubtypeConstraint, Range
from relationalai.early_access.dsl.orm.models import Model
from relationalai.early_access.dsl.orm.relationships import Role
from relationalai.early_access.dsl.orm.types import Concept
from relationalai.early_access.metamodel.util import Printer as BasePrinter, OrderedSet
import relationalai.early_access.builder as qb

class Printer(BasePrinter):
    _unique_constraints: OrderedSet[Unique]
    _mandatory_constraints: OrderedSet[Mandatory]
    _role_value_constraints: OrderedSet[RoleValueConstraint]
    _inclusive_subtype_constraints: OrderedSet[InclusiveSubtypeConstraint]
    _exclusive_subtype_constraints: OrderedSet[ExclusiveSubtypeConstraint]

    def __init__(self, io: typing.Optional[typing.IO[str]] = None):
        # Set the base class field (frozen)
        object.__setattr__(self, 'io', io)

        # Set all mutable fields using object.__setattr__
        object.__setattr__(self, '_unique_constraints', OrderedSet())
        object.__setattr__(self, '_mandatory_constraints', OrderedSet())
        object.__setattr__(self, '_role_value_constraints', OrderedSet())
        object.__setattr__(self, '_inclusive_subtype_constraints', OrderedSet())
        object.__setattr__(self, '_exclusive_subtype_constraints', OrderedSet())


    def to_string(self, model: Model) -> None:
        self._process_constraints(model)

        self._print_nl("import relationalai.early_access.builder as qb")
        self._print_nl("from relationalai.early_access.dsl.orm.models import Model")
        self._print_nl("from relationalai.early_access.dsl.orm.constraints import Range")
        self._nl()

        self._print_nl(f"model = Model(name='{model.name}', is_primary={model.is_primary}"
                       f"{self._print_if_true('dry_run', model.qb_model()._dry_run)})")
        self._print_nl("Concept = model.Concept")
        self._print_nl("Relationship = model.Relationship")
        self._print_nl("Unique = model.unique")
        self._print_nl("Mandatory = model.mandatory")
        self._print_nl("RoleValueConstraint = model.role_value_constraint")
        self._print_nl("InclusiveSubtypeConstraint = model.inclusive_subtype_constraint")
        self._print_nl("ExclusiveSubtypeConstraint = model.exclusive_subtype_constraint")

        self._nl()
        self._handle_concepts(model)

        self._nl()
        self._handle_relationships(model)

        self._nl()
        self._handle_ref_schemes(model)

        self._nl()
        self._handle_uniqueness_constraints()

        self._nl()
        self._handle_mandatory_constraints()

        self._nl()
        self._handle_role_value_constraints()

        self._nl()
        self._handle_subtype_constraints()

    def _handle_concepts(self, model: Model) -> None:
        concepts_map = model.concepts_map()
        sorted_concepts = self._sort_dependency_graph(model.concepts())
        for name in sorted_concepts:
            c = concepts_map.get(name)
            if c is None:
                raise ValueError(f"The concept '{name}' was not declared but used as concept domain.")

            extends = c._extends
            extends_elements = [f"{self._get_type(ext)}" for ext in extends]
            extends_str = f", extends=[{', '.join(extends_elements)}]" if extends else ""
            self._print_nl(f"{name} = Concept('{name}'{extends_str})")

    def _handle_relationships(self, model: Model) -> None:
        for rel in model.relationships():
            # print a root Relationship
            self._print_nl(f"{self._get_relationship_name(rel)} = "
                           f"Relationship('{rel._madlib}'{self._print_if_not_empty_and_not_equal('short_name', rel._passed_short_name, rel._name)})")
            # print remaining RelationshipReadings if any
            for r in rel._readings[1:]:
                self._print_nl(f"{self._get_relationship_name(r)} = "
                               f"{self._get_relationship_name(rel)}.alt('{r._madlib}'{self._print_if_not_empty_and_not_equal('short_name', r._passed_short_name, r._name)})")

    def _handle_ref_schemes(self, model: Model) -> None:
        for concept_name, concept in model.entity_types_map().items():
            if not isinstance(concept, Concept) or not concept._reference_schemes:
                continue

            for ref_scheme in concept._reference_schemes:
                rel_names = [self._get_relationship_name(rel) for rel in ref_scheme]
                self._print_nl(f"{concept_name}.identify_by({', '.join(rel_names)})")

    def _handle_uniqueness_constraints(self) -> None:
        for constraint in self._unique_constraints:
            if not constraint.is_preferred_identifier:
                elements = []
                for role in constraint.roles():
                    elements.append(self._get_role_name(role))
                self._print_nl(f"Unique({', '.join(elements)})")

    def _handle_mandatory_constraints(self):
        for constraint in self._mandatory_constraints:
            role = constraint.roles()[0]
            role_name = self._get_role_name(role)
            self._print_nl(f"Mandatory({role_name})")

    def _handle_role_value_constraints(self) -> None:
        for constraint in self._role_value_constraints:
            role = constraint.roles()[0]
            elements = []

            for value in constraint.values():
                if isinstance(value, Range):
                    if value._start is not None and value._end is not None:
                        elements.append(f"Range.between({value._start}, {value._end})")
                    elif value._end is not None:
                        elements.append(f"Range.to_value({value._end})")
                    else:
                        elements.append(f"Range.from_value({value._start})")
                elif isinstance(value, str):
                    elements.append(repr(value))
                else:
                    elements.append(str(value))

            role_name = self._get_role_name(role)
            self._print_nl(f"RoleValueConstraint({role_name}, [{', '.join(elements)}])")

    def _handle_subtype_constraints(self):
        self._emit_subtype_constraints(self._inclusive_subtype_constraints, "InclusiveSubtypeConstraint")
        self._nl()
        self._emit_subtype_constraints(self._exclusive_subtype_constraints, "ExclusiveSubtypeConstraint")

    def _emit_subtype_constraints(self, constraints, constraint_type: str):
        for constraint in constraints:
            concepts = [self._get_type(c) for c in constraint.concepts()]
            self._print_nl(f"{constraint_type}({', '.join(concepts)})")

    def _process_constraints(self, model: Model) -> None:
        for c in model.constraints():
            if isinstance(c, Unique):
                self._unique_constraints.add(c)
            elif isinstance(c, Mandatory):
                self._mandatory_constraints.add(c)
            elif isinstance(c, RoleValueConstraint):
                self._role_value_constraints.add(c)
            elif isinstance(c, InclusiveSubtypeConstraint):
                self._inclusive_subtype_constraints.add(c)
            elif isinstance(c, ExclusiveSubtypeConstraint):
                self._exclusive_subtype_constraints.add(c)

    def _get_role_name(self, role: Role) -> str:
        return f"{self._get_relationship_name(role._relationship)}['{role._field_ref._name}']"

    def _sort_dependency_graph(self, concepts: list[qb.Concept]):
        nodes = []
        edges = []
        for concept in concepts:
            name = concept._name
            nodes.append(name)
            for ext in concept._extends:
                if not self._is_builtin_type(ext):
                    edges.append((ext._name, name))
        return topological_sort(nodes, edges)

    @staticmethod
    def _get_relationship_name(rel: typing.Union[qb.Relationship, qb.RelationshipReading]) -> str:
        if rel._parent and rel._short_name:
            parent_name = rel._parent._name
            prefix = "qb." if parent_name in Concept.builtins else ""
            return f"{prefix}{parent_name}.{rel._short_name}"
        return rel._name

    def _get_type(self, t: Concept) -> str:
        name = self._get_concept_name(t)
        return f"qb.{name}" if name in Concept.builtins else name

    def _is_builtin_type(self, t: Concept) -> bool:
        return self._get_concept_name(t) in Concept.builtins

    @staticmethod
    def _get_concept_name(t: Concept) -> str:
        return 'Integer' if t._name == 'Int' else t._name

    @staticmethod
    def _print_if_not_empty(label: str, value: typing.Optional[str]) -> str:
        return f", {label}='{value}'" if value else ""

    @staticmethod
    def _print_if_not_empty_and_not_equal(label: str, value: typing.Optional[str], compare_to: typing.Optional[str]) -> str:
        return f", {label}='{value}'" if value and value != compare_to else ""

    @staticmethod
    def _print_if_true(label: str, value: bool) -> str:
        return f", {label}=True" if value else ""