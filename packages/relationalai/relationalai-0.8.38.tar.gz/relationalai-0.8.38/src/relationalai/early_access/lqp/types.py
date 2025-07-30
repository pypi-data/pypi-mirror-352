from relationalai.early_access.metamodel import ir as meta
from relationalai.early_access.metamodel import types
from relationalai.early_access.lqp import ir as lqp
import datetime

def meta_type_to_lqp(typ: meta.Type) -> lqp.RelType:
    if isinstance(typ, meta.UnionType):
        # TODO - this is WRONG! we need to fix the typer wrt overloading
        typ = typ.types.some()

    assert isinstance(typ, meta.ScalarType)

    if types.is_builtin(typ):
        # TODO: just ocompare to types.py
        if typ.name == "Int":
            return lqp.PrimitiveType.INT
        elif typ.name == "Float":
            return lqp.PrimitiveType.FLOAT
        elif typ.name == "String":
            return lqp.PrimitiveType.STRING
        elif typ.name == "Number":
            # TODO: fix this, this is wrong
            return lqp.PrimitiveType.INT
        elif typ.name == "Decimal":
            return lqp.RelValueType.DECIMAL
        elif typ.name == "Date":
            return lqp.RelValueType.DATE
        elif typ.name == "DateTime":
            return lqp.RelValueType.DATETIME
        elif typ.name == "RowId":
            return lqp.PrimitiveType.UINT128
        elif types.is_any(typ):
            return lqp.PrimitiveType.UNSPECIFIED
        else:
            raise NotImplementedError(f"Unknown builtin type: {typ.name}")
    elif types.is_entity_type(typ):
        return lqp.PrimitiveType.UINT128
    else:
        # Otherwise, the type extends some other type, we use that instead
        assert len(typ.super_types) > 0, f"Type {typ} has no super types"
        assert len(typ.super_types) == 1, f"Type {typ} has multiple super types: {typ.super_types}"
        super_type = typ.super_types[0]
        assert isinstance(super_type, meta.ScalarType), f"Super type {super_type} of {typ} is not a scalar type"
        assert types.is_builtin(super_type), f"Super type {super_type} of {typ} is not a builtin type"
        return meta_type_to_lqp(super_type)

def type_from_constant(arg: lqp.PrimitiveValue) -> lqp.RelType:
    if isinstance(arg, int):
        return lqp.PrimitiveType.INT
    elif isinstance(arg, float):
        return lqp.PrimitiveType.FLOAT
    elif isinstance(arg, str):
        return lqp.PrimitiveType.STRING
    elif isinstance(arg, lqp.UInt128):
        return lqp.PrimitiveType.UINT128
    # TODO: Direct use of date/datetime is not supported in the IR, so this should be
    # rewritten with construct_date.
    elif isinstance(arg, datetime.date):
        return lqp.RelValueType.DATE
    else:
        raise NotImplementedError(f"Unknown constant type: {type(arg)}")
