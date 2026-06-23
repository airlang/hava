from dataclasses import dataclass
from enum import Enum, auto


class OpCode(Enum):
    LOAD_CONST = auto()
    LOAD_NAME = auto()
    STORE_NAME = auto()
    PRINT = auto()
    POP = auto()
    EQ = auto()
    GTE = auto()
    LTE = auto()
    ADD = auto()
    SUB = auto()
    MUL = auto()
    DIV = auto()
    JUMP = auto()
    JUMP_IF_FALSE = auto()


@dataclass
class Instruction:
    op: OpCode
    arg: object = None
