from dataclasses import dataclass, field
from .builtin import BUILTINS
from .bytecode import OpCode, HavaFunction, HavaBuiltinFunction
from .errors import HavaRuntimeError


@dataclass
class Frame:
    instructions: list
    ip: int = 0
    stack: list = field(default_factory=list)
    locals: dict = field(default_factory=dict)
    name: str = "<frame>"

class HavaVM:
    def __init__(self):
        self.globals = BUILTINS.copy()
        self.frames = []

    def resolve_name(self, frame, name):
        if name in frame.locals:
            return frame.locals[name]
        if name in self.globals:
            return self.globals[name]
        raise HavaRuntimeError(f"Bilinmeyen değişken: {name}")

    def run(self, instructions):
        frame = Frame(
            instructions=instructions,
            locals=self.globals,
            name="<module>"
        )
        return self.run_frame(frame)

    def run_frame(self, frame):
        self.frames.append(frame)
        instructions = frame.instructions
        try:
            while frame.ip < len(instructions):
                instruction = instructions[frame.ip]
                op = instruction.op
                arg = instruction.arg
                if op == OpCode.LOAD_CONST:
                    frame.stack.append(arg)
                elif op == OpCode.LOAD_NAME:
                    frame.stack.append(self.resolve_name(frame, arg))
                elif op == OpCode.STORE_NAME:
                    value = frame.stack.pop()
                    frame.locals[arg] = value
                elif op == OpCode.ADD:
                    b = frame.stack.pop()
                    a = frame.stack.pop()
                    frame.stack.append(a + b)
                elif op == OpCode.SUB:
                    b = frame.stack.pop()
                    a = frame.stack.pop()
                    frame.stack.append(a - b)
                elif op == OpCode.MUL:
                    b = frame.stack.pop()
                    a = frame.stack.pop()
                    frame.stack.append(a * b)
                elif op == OpCode.DIV:
                    b = frame.stack.pop()
                    a = frame.stack.pop()
                    frame.stack.append(a / b)
                elif op == OpCode.EQ:
                    b = frame.stack.pop()
                    a = frame.stack.pop()
                    frame.stack.append(a == b)
                elif op == OpCode.GTE:
                    b = frame.stack.pop()
                    a = frame.stack.pop()
                    frame.stack.append(a >= b)
                elif op == OpCode.LTE:
                    b = frame.stack.pop()
                    a = frame.stack.pop()
                    frame.stack.append(a <= b)
                elif op == OpCode.POP:
                    frame.stack.pop()
                elif op == OpCode.JUMP:
                    ip = arg
                    continue
                elif op == OpCode.JUMP_IF_FALSE:
                    condition = frame.stack.pop()
                    if not condition:
                        ip = arg
                        continue
                elif op == OpCode.CALL:
                    name, arg_count = arg
                    args = [frame.stack.pop() for _ in range(arg_count)]
                    args.reverse()
                    fn = self.resolve_name(frame, name)
                    if isinstance(fn, HavaBuiltinFunction):
                        if fn.params is not None and fn.params != len(args):
                            raise HavaRuntimeError(
                                f"{name} fonksiyonu {fn.params} argüman bekliyor, "
                                f"{len(args)} verildi."
                            )
                        try:
                            result = fn.func(*args)
                        except Exception as e:
                            raise HavaRuntimeError(f"{name} çalışırken hata oluştu: {e}")
                        frame.stack.append(result)
                    elif isinstance(fn, HavaFunction):
                        if len(fn.params) != len(args):
                            raise HavaRuntimeError(
                                f"{name} fonksiyonu {len(fn.params)} argüman bekliyor, "
                                f"{len(args)} verildi."
                            )
                        local_vars = {}
                        for param_name, arg_value in zip(fn.params, args):
                            local_vars[param_name] = arg_value
                        function_frame = Frame(
                            instructions=fn.instructions,
                            locals=local_vars,
                            name=name
                        )
                        result = self.run_frame(function_frame)
                        frame.stack.append(result)
                    else:
                        raise HavaRuntimeError(f"{name} bir fonksiyon değil")
                elif op == OpCode.RETURN:
                    if frame.stack:
                        return frame.stack.pop()
                    return None
                elif op == OpCode.NEG:
                    value = frame.stack.pop()
                    frame.stack.append(-value)
                elif op == OpCode.INDEX:
                    index = frame.stack.pop()
                    target = frame.stack.pop()
                    try:
                        frame.stack.append(target[index])
                    except KeyError:
                        raise HavaRuntimeError("Dict içinde bu key bulunamadı.")
                    except IndexError:
                        raise HavaRuntimeError("Index sınır dışında.")
                    except TypeError:
                        raise HavaRuntimeError("Bu değer indexlenemez.")
                elif op == OpCode.BUILD_ARRAY:
                    elems = [frame.stack.pop() for _ in range(arg)]
                    elems.reverse()
                    frame.stack.append(elems)
                elif op == OpCode.INDEX_ASSIGN:
                    value = frame.stack.pop()
                    index = frame.stack.pop()
                    target = frame.stack.pop()
                    if not isinstance(target, (list, dict)):
                        raise HavaRuntimeError("Sadece array veya dict üzerinde index assignment yapılabilir.")
                    try:
                        target[index] = value
                    except IndexError:
                        raise HavaRuntimeError("Array index sınır dışında.")
                    except TypeError:
                        raise HavaRuntimeError("Geçersiz index/key değeri.")
                elif op == OpCode.BUILD_DICT:
                    result = {}
                    for _ in range(arg):
                        value = frame.stack.pop()
                        key = frame.stack.pop()
                        result[key] = value
                    frame.stack.append(result)
                else:
                    raise HavaRuntimeError(f"Bilinmeyen opcode: {op}")
                frame.ip += 1
            return None
        finally:
            self.frames.pop()