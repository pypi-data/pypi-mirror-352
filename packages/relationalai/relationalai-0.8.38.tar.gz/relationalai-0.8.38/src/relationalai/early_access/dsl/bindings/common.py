from abc import abstractmethod
from typing import Optional

from relationalai.early_access.dsl.core.types.unconstrained import UnconstrainedValueType


class BindableTable:
    """
    A class representing a bindable table.
    """

    _table_name: str

    def __init__(self, name: str):
        self._table_name = name

    @property
    def table_name(self):
        return self._table_name

    @abstractmethod
    def key_type(self) -> UnconstrainedValueType:
        pass

    @abstractmethod
    def physical_name(self) -> str:
        pass


class BindableAttribute:

    @property
    @abstractmethod
    def table(self) -> BindableTable:
        pass

    @abstractmethod
    def physical_name(self) -> str:
        pass

    @abstractmethod
    def type(self) -> UnconstrainedValueType:
        pass

    @abstractmethod
    def decimal_scale(self) -> Optional[int]:
        pass

    @abstractmethod
    def decimal_size(self) -> Optional[int]:
        pass
