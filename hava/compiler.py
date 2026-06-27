from .builtin import BUILTINS
from .bytecode import OpCode, Instruction, HavaFunction
from .errors import HavaCompilerError

def ensure_not_builtin_name(name):
    if name in set(BUILTINS.keys()):
        raise HavaCompilerError(
            f"{name!r} yerleşik bir fonksiyon adı olduğu için kullanılamaz."
        )

class HavaCompiler:
    def __init__(self):
        self.instructions = []

    def compile(self, ast):
        self.instructions = []
        self.visit(ast)
        return self.instructions

    def emit(self, op, arg=None):
        instruction = Instruction(op, arg)
        self.instructions.append(instruction)
        return len(self.instructions) - 1

    def patch(self, index, arg):
        self.instructions[index].arg = arg

    def visit(self, ast):
        if ast is None:
            return None
        if isinstance(ast, (int, float, str, bool)):
            self.emit(OpCode.LOAD_CONST, ast)
            return None
        method = getattr(self, f"visit_{ast[0]}", None)
        if method is None:
            raise HavaCompilerError(f"Bilinmeyen AST node tipi: {ast[0]}")
        return method(ast)

    def visit_program(self, ast):
        statements = ast[1]
        for statement in statements:
            self.visit(statement)

    def visit_block(self, ast):
        statements = ast[1]
        for statement in statements:
            self.visit(statement)

    def visit_num(self, ast):
        self.emit(OpCode.LOAD_CONST, ast[1])

    def visit_str(self, ast):
        self.emit(OpCode.LOAD_CONST, ast[1])

    def visit_var(self, ast):
        name = ast[1]
        self.emit(OpCode.LOAD_NAME, name)

    def visit_dict(self, ast):
        for key, value in ast[1]:
            self.visit(key)
            self.visit(value)
        self.emit(OpCode.BUILD_DICT, len(ast[1]))

    def visit_array(self, ast):
        for elem in ast[1]:
            self.visit(elem)
        self.emit(OpCode.BUILD_ARRAY, len(ast[1]))

    def visit_index(self, ast):
        self.visit(ast[1])
        self.visit(ast[2])
        self.emit(OpCode.INDEX)

    def visit_index_assign(self, ast):
        ast_info = {'array_name': ast[1], 'array_index': ast[2], "to_assign": ast[3]}
        self.visit(ast_info["array_name"])
        self.visit(ast_info["array_index"])
        self.visit(ast_info["to_assign"])
        self.emit(OpCode.INDEX_ASSIGN)

    def visit_assign(self, ast):
        name = ast[1]
        value = ast[2]
        ensure_not_builtin_name(name)
        self.visit(value)
        self.emit(OpCode.STORE_NAME, name)

    def visit_print(self, ast):
        value = ast[1]
        self.visit(value)
        self.emit(OpCode.PRINT)

    def visit_binary(self, ast):
        opcodes = {
            '+': OpCode.ADD,
            '-': OpCode.SUB,
            '*': OpCode.MUL,
            '/': OpCode.DIV,
            '==': OpCode.EQ,
            '>=': OpCode.GTE,
            '<=': OpCode.LTE,
        }
        op = ast[1]
        left = ast[2]
        right = ast[3]
        self.visit(left)
        self.visit(right)

        if op not in opcodes:
            raise HavaCompilerError(f"Bilinmeyen binary operatör: {op}")
        self.emit(opcodes[op])

    def visit_if(self, ast):
        ast_info = {"condition": ast[1], "then_block": ast[2]}
        self.visit(ast_info["condition"])
        jump_if_false_index = self.emit(OpCode.JUMP_IF_FALSE, None)
        self.visit(ast_info["then_block"])
        end_index = len(self.instructions)
        self.patch(jump_if_false_index, end_index)

    def visit_if_else(self, ast):
        ast_info = {"condition": ast[1], "then_block": ast[2], "else_block": ast[3]}
        self.visit(ast_info["condition"])
        jump_to_else_index = self.emit(OpCode.JUMP_IF_FALSE, None)
        self.visit(ast_info["then_block"])
        jump_to_end_index = self.emit(OpCode.JUMP, None)
        else_index = len(self.instructions)
        self.patch(jump_to_else_index, else_index)
        self.visit(ast_info["else_block"])
        end_index = len(self.instructions)
        self.patch(jump_to_end_index, end_index)

    def visit_fun_def(self, ast):
        ensure_not_builtin_name(ast[1])
        for param in ast[2]:
            ensure_not_builtin_name(param)
        outer_instructions = self.instructions
        self.instructions = []
        self.visit(ast[3])
        self.emit(OpCode.LOAD_CONST, None)
        self.emit(OpCode.RETURN)
        function_instructions = self.instructions
        self.instructions = outer_instructions
        function = HavaFunction(ast[2], function_instructions)
        self.emit(OpCode.LOAD_CONST, function)
        self.emit(OpCode.STORE_NAME, ast[1])

    def visit_fun_call(self, ast):
        for arg in ast[2]:
            self.visit(arg)
        self.emit(OpCode.CALL, (ast[1], len(ast[2])))

    def visit_expr_stmt(self, ast):
        self.visit(ast[1])
        self.emit(OpCode.POP)

    def visit_return(self, ast):
        self.visit(ast[1])
        self.emit(OpCode.RETURN)

    def visit_aug_assign(self, ast):
        name = ast[1]
        op = ast[2]
        value = ast[3]
        ensure_not_builtin_name(name)
        self.emit(OpCode.LOAD_NAME, name)
        self.visit(value)
        if op == '+=':
            self.emit(OpCode.ADD)
        elif op == '-=':
            self.emit(OpCode.SUB)
        else:
            raise HavaCompilerError(f"Bilinmeyen atama operatörü: {op}")
        self.emit(OpCode.STORE_NAME, name)

    def visit_neg(self, ast):
        self.visit(ast[1])
        self.emit(OpCode.NEG)
