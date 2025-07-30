from relationalai.early_access.dsl import AssertedRelation, RelationSignature
from relationalai.early_access.dsl.bindings.common import BindableAttribute


class AttributeView(AssertedRelation):
    """
    A class representing an attribute view relation.
    """

    def __init__(self, namespace, attr: BindableAttribute):
        name = self._get_relation_name(attr)
        sig = self._get_relation_signature(attr)
        super().__init__(namespace, name, sig)
        self._attr = attr

    @staticmethod
    def _get_relation_name(attr: BindableAttribute):
        """
        Returns the relation name of the attribute view, combining table name and attribute name.
        """
        attr_name = attr.physical_name()
        table_name = attr.table.physical_name()
        name = f"{table_name}:{attr_name}"
        return name

    @staticmethod
    def _get_relation_signature(attr: BindableAttribute):
        """
        Returns the relation signature of the attribute view.
        """
        sig = RelationSignature(attr.table.key_type(), attr.type())
        return sig

    def attr(self):
        """
        Returns the attribute of the attribute view.
        """
        return self._attr

    def __repr__(self):
        return f"AttributeView({self.qualified_name()})"
