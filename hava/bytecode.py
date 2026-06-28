from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import Callable


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
    NEG = auto()
    CALL = auto()
    RETURN = auto()
    JUMP = auto()
    JUMP_IF_FALSE = auto()
    INDEX = auto()
    BUILD_ARRAY = auto()
    INDEX_ASSIGN = auto()
    BUILD_DICT = auto()
    GET_ITER = auto()
    FOR_ITER = auto()


@dataclass
class Instruction:
    op: OpCode
    arg: object = None

@dataclass
class HavaFunction:
    params: list
    instructions: list


@dataclass
class HavaBuiltinFunction:
    name: str
    func: Callable
    params: int | None = None