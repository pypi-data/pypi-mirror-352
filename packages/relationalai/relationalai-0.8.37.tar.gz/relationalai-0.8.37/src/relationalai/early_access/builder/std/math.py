from __future__ import annotations
from typing import Any, Union

from .. import builder as b

_Number = Union[b.Producer, float, int]
_Integer = Union[b.Producer, int]

def _make_expr(op: str, *args: Any) -> b.Expression:
    return b.Expression(b.Relationship.builtins[op], *args)

def abs(value: _Number) -> b.Expression:
    return _make_expr("abs", value, b.Number.ref("res"))
