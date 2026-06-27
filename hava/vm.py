from .bytecode import OpCode, HavaFunction
from .errors import HavaRuntimeError


class HavaVM:
    def __init__(self):
        self.stack = []
        self.env = {}

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
                if not isinstance(fn, HavaFunction):
                    raise HavaRuntimeError(f"{name} bir fonksiyon değil")
                if len(fn.params) != len(args):
                    raise HavaRuntimeError(
                        f"{name} fonksiyonu {len(fn.params)} argüman bekliyor, "
                        f"{len(args)} verildi."
                    )
                old_env = self.env.copy()
                for param_name, arg_value in zip(fn.params, args):
                    self.env[param_name] = arg_value
                result = self.run(fn.instructions)
                self.env = old_env
                self.stack.append(result)
            elif op == OpCode.RETURN:
                if self.stack:
                    return self.stack.pop()
                return None
            elif op == OpCode.NEG:
                value = self.stack.pop()
                self.stack.append(-value)
            else:
                raise HavaRuntimeError(f"Bilinmeyen opcode: {op}")

            ip += 1
