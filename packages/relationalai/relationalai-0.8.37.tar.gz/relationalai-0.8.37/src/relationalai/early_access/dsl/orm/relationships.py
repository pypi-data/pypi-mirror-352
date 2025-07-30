from typing import Optional, Any, Union

from relationalai.early_access.builder import Relationship as QBRelationship
from relationalai.early_access.builder.builder import Concept, RelationshipFieldRef, Field
from relationalai.early_access.dsl.core.utils import generate_stable_uuid


class Relationship(QBRelationship):

    def __init__(self, model, reading:Any, short_name:str="", fields:Optional[list[Field]]=None):
        super().__init__(reading, short_name=short_name, model=model.qb_model(), fields=fields)
        self._dsl_model = model

    def __getitem__(self, arg:Union[str, int, Concept]) -> Any:
        return Role._from_field(super().__getitem__(arg))

    def _guid(self):
        return generate_stable_uuid(str(self._id))

    def _arity(self):
        return len(self._fields)

    def _binary(self):
        return self._arity() == 2

    def _first(self):
        return self.__getitem__(0)

class Role(RelationshipFieldRef):
    _sibling: Optional['Role'] = None
    _prefix: Optional[str] = None
    _postfix: Optional[str] = None

    def __init__(self, parent:Any, part_of, pos):
        super().__init__(parent, part_of, pos)

    def _guid(self):
        return generate_stable_uuid(f"{self._field_ix}_{self._part_of()._guid()}")

    def player(self) -> Concept:
        return self._concept

    def sibling(self):
        if self._relationship._arity() == 2 and not self._sibling:
            first_role = self._relationship[0]
            sibling = self._relationship[1] if self._id == first_role._id else first_role
            self._sibling = sibling
        return self._sibling

    def _part_of(self):
        return self._relationship

    def verbalization(self, prefix: Optional[str] = None, postfix: Optional[str] = None):
        self._prefix = prefix
        self._postfix = postfix

    def verbalize(self):
        text_frags = []
        if self._prefix is not None:
            text_frags.append(f"{self._prefix}-")
        text_frags.append(f"{str(self.player())}")
        if self._postfix is not None:
            text_frags.append(f"-{self._postfix}")
        return " ".join(text_frags)

    @property
    def postfix(self) -> Optional[str]:
        return self._postfix

    @property
    def prefix(self) -> Optional[str]:
        return self._prefix

    @staticmethod
    def _from_field(field:RelationshipFieldRef):
        return Role(field._parent, field._relationship, field._field_ix)
