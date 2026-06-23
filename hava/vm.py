from .bytecode import OpCode


class HavaVM:
    def __init__(self):
        self.stack = []
        self.env = {}
        self.ip = 0

    def run(self, instructions):
        self.ip = 0

        while self.ip < len(instructions):
            op = instructions[self.ip].op
            arg = instructions[self.ip].arg

            if op == OpCode.LOAD_CONST:
                self.stack.append(arg)
            elif op == OpCode.LOAD_NAME:
                if arg not in self.env:
                    raise RuntimeError(f"Bilinmeyen değişken: {arg}")
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
                self.ip = arg
                continue
            elif op == OpCode.JUMP_IF_FALSE:
                condition = self.stack.pop()
                if not condition:
                    self.ip = arg
                    continue
            else:
                raise RuntimeError(f"Bilinmeyen opcode: {op}")

            self.ip += 1
