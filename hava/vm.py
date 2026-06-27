from .builtin import BUILTINS
from .bytecode import OpCode, HavaFunction, HavaBuiltinFunction
from .errors import HavaRuntimeError


class HavaVM:
    def __init__(self):
        self.stack = []
        self.env = BUILTINS.copy()

    def run(self, instructions):
        ip = 0
        while ip < len(instructions):
            op = instructions[ip].op
            arg = instructions[ip].arg
            if op == OpCode.LOAD_CONST:
                self.stack.append(arg)
            elif op == OpCode.LOAD_NAME:
                if arg not in self.env:
                    raise HavaRuntimeError(f"Bilinmeyen değişken: {arg}")
                self.stack.append(self.env[arg])
            elif op == OpCode.STORE_NAME:
                if arg in set(BUILTINS.keys()):
                    raise HavaRuntimeError(
                        f"{arg!r} yerleşik bir fonksiyon adı olduğu için değiştirilemez."
                    )
                value = self.stack.pop()
                self.env[arg] = value
            elif op == OpCode.ADD:
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.append(a + b)
            elif op == OpCode.SUB:
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.append(a - b)
            elif op == OpCode.MUL:
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.append(a * b)
            elif op == OpCode.DIV:
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.append(a / b)
            elif op == OpCode.EQ:
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.append(a == b)
            elif op == OpCode.GTE:
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.append(a >= b)
            elif op == OpCode.LTE:
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.append(a <= b)
            elif op == OpCode.PRINT:
                value = self.stack.pop()
                print(value)
            elif op == OpCode.POP:
                self.stack.pop()
            elif op == OpCode.JUMP:
                ip = arg
                continue
            elif op == OpCode.JUMP_IF_FALSE:
                condition = self.stack.pop()
                if not condition:
                    ip = arg
                    continue
            elif op == OpCode.CALL:
                name, arg_count = arg
                args = [self.stack.pop() for _ in range(arg_count)]
                args.reverse()
                if name not in self.env:
                    raise HavaRuntimeError(f"Bilinmeyen fonksiyon: {name}")
                fn = self.env[name]
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
                    self.stack.append(result)
                elif isinstance(fn, HavaFunction):
                    if len(fn.params) != len(args):
                        raise HavaRuntimeError(
                            f"{name} fonksiyonu {len(fn.params)} argüman bekliyor, "
                            f"{len(args)} verildi."
                        )
                    old_env = self.env.copy()
                    try:
                        for param_name, arg_value in zip(fn.params, args):
                            self.env[param_name] = arg_value
                        result = self.run(fn.instructions)
                    finally:
                        self.env = old_env
                    self.stack.append(result)
                else:
                    raise HavaRuntimeError(f"{name} bir fonksiyon değil")
            elif op == OpCode.RETURN:
                if self.stack:
                    return self.stack.pop()
                return None
            elif op == OpCode.NEG:
                value = self.stack.pop()
                self.stack.append(-value)
            elif op == OpCode.INDEX:
                index = self.stack.pop()
                target = self.stack.pop()
                try:
                    self.stack.append(target[index])
                except KeyError:
                    raise HavaRuntimeError("Dict içinde bu key bulunamadı.")
                except IndexError:
                    raise HavaRuntimeError("Index sınır dışında.")
                except TypeError:
                    raise HavaRuntimeError("Bu değer indexlenemez.")
            elif op == OpCode.BUILD_ARRAY:
                elems = [self.stack.pop() for _ in range(arg)]
                elems.reverse()
                self.stack.append(elems)
            elif op == OpCode.INDEX_ASSIGN:
                value = self.stack.pop()
                index = self.stack.pop()
                target = self.stack.pop()
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
                    value = self.stack.pop()
                    key = self.stack.pop()
                    result[key] = value
                self.stack.append(result)
            else:
                raise HavaRuntimeError(f"Bilinmeyen opcode: {op}")
            ip += 1
