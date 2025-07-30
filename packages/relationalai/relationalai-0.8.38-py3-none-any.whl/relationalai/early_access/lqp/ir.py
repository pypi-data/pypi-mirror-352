from __future__ import annotations
from dataclasses import dataclass
from typing import Union, Tuple

__all__ = [
    "SourceInfo",
    "LqpNode",
    "Declaration",
    "Def",
    "Loop",
    "Abstraction",
    "Formula",
    "Exists",
    "Reduce",
    "Conjunction",
    "Disjunction",
    "Not",
    "FFI",
    "Atom",
    "Pragma",
    "Primitive",
    "RelAtom",
    "Cast",
    "Var",
    "UInt128",
    "PrimitiveValue",
    "Constant",
    "Term",
    "Specialized",
    "RelTerm",
    "Attribute",
    "RelationId",
    "RelValueType",
    "PrimitiveType",
    "RelType",
    "FragmentId",
    "Fragment",
    "Define",
    "Write",
    "Output",
    "Read",
    "Epoch",
    "Transaction",
    "DebugInfo",
    "LqpProgram",
    "lqp_node_to_proto",
    "ir_to_proto",
    "convert_transaction",
    "var"
]

from lqp.ir import (
    SourceInfo,
    LqpNode,
    Declaration,
    Def,
    Loop,
    Abstraction,
    Formula,
    Exists,
    Reduce,
    Conjunction,
    Disjunction,
    Not,
    FFI,
    Atom,
    Pragma,
    Primitive,
    RelAtom,
    Cast,
    Var,
    UInt128,
    PrimitiveValue,
    Constant,
    Term,
    Specialized,
    RelTerm,
    Attribute,
    RelationId,
    RelValueType,
    PrimitiveType,
    RelType,
    FragmentId,
    Fragment,
    Define,
    Write,
    Output,
    Read,
    Epoch,
    Transaction
)

from lqp.emit import (
    ir_to_proto,
    convert_transaction
)

def var(name: str, meta: Union[SourceInfo, None] = None) -> Var:
    return Var(name=name, meta=meta)

@dataclass(frozen=True)
class DebugInfo:
    id_to_orig_name: dict[RelationId, str]

@dataclass(frozen=True)
class LqpProgram:
    defs: list[Declaration]
    outputs: list[Tuple[str, RelationId]]
    debug_info: Union[DebugInfo, None] = None

def lqp_program_to_transaction(program: LqpProgram, fragment_name: bytes = bytes(404)) -> Transaction:
    lqp_ir_fragment_id = FragmentId(id=fragment_name, meta=None)
    lqp_ir_fragment = Fragment(id=lqp_ir_fragment_id, declarations=program.defs, meta=None)
    lqp_ir_define_op = Define(fragment=lqp_ir_fragment, meta=None)
    lqp_ir_write = Write(write_type=lqp_ir_define_op, meta=None)
    lqp_ir_reads = []
    for name, rid in program.outputs:
        lqp_ir_output = Output(name=name, relation_id=rid, meta=None)
        lqp_ir_reads.append(Read(read_type=lqp_ir_output, meta=None))
    lqp_ir_epoch = Epoch(local_writes=[lqp_ir_write], reads=lqp_ir_reads, persistent_writes=[], meta=None)
    return Transaction(epochs=[lqp_ir_epoch], meta=None)

lqp_node_to_proto = ir_to_proto
