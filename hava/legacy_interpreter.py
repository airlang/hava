from .sly import Parser
from .sly import Lexer

KEYWORDS = {
    "eğer": "IF",
    "eger": "IF",
    "if": "IF",

    "değilse": "ELSE",
    "degilse": "ELSE",
    "else": "ELSE",

    "döngü": "FOR",
    "dongu": "FOR",
    "for": "FOR",

    "fonksiyon": "FUN",
    "function": "FUN",
    "fun": "FUN",

    "içinde": "IN",
    "icinde": "IN",
    "in": "IN",

    "yaz": "PRINT",
    "print": "PRINT",
}
OPERATORS = {
    "::": "START_PREFIX",
    ":": "FINISH_PREFIX",

    "+=": "PLUSEQ",
    "-=": "MINUSEQ",

    "==": "EQEQ",
    ">=": "HIGHEQ",
    "<=": "LOWEQ",

    "=": "EQ",
}


class HavaLexer(Lexer):
    ignore = " \t"
    global KEYWORDS, OPERATORS
    literals = {"+", "-", "*", "/", "(", ")", ","}

    tokens = {
        "NAME",
        "NUMBER",
        "STRING",
        "OPERATOR",
        *set(OPERATORS.values()),
        *set(KEYWORDS.values()),
    }

    @_(r"::|\+=|-=|==|>=|<=|:|=")
    def OPERATOR(self, t):
        t.type = OPERATORS[t.value]
        return t

    @_(r'"([^"\\]|\\.)*"|\'([^\'\\]|\\.)*\'')
    def STRING(self, t):
        t.value = t.value[1:-1]
        return t

    @_(r"\d+")
    def NUMBER(self, t):
        t.value = int(t.value)
        return t

    @_(r"[a-zA-ZğüşöçıİĞÜŞÖÇ_][a-zA-Z0-9ğüşöçıİĞÜŞÖÇ_]*")
    def NAME(self, t):
        global KEYWORDS
        t.type = KEYWORDS.get(t.value, "NAME")
        return t

    @_(r"##.*##")
    def COMMENT(self, t):
        pass

    def error(self, t):
        print(f"Geçersiz karakter: {t.value[0]!r}")
        self.index += 1


class HavaParser(Parser):
    tokens = HavaLexer.tokens
    start = 'program'

    precedence = (
        ('left', '+', '-'),
        ('left', '*', '/'),
        ('right', 'UMINUS'),
    )

    @_('statements')
    def program(self, p):
        return ('program', p.statements)

    @_('statement')
    def statements(self, p):
        return [p.statement]

    @_('statements statement')
    def statements(self, p):
        return p.statements + [p.statement]

    @_('START_PREFIX statements FINISH_PREFIX')
    def block(self, p):
        return ('block', p.statements)

    @_('NAME EQ expr FINISH_PREFIX')
    def statement(self, p):
        return ('assign', p.NAME, p.expr)

    @_('PRINT "(" expr ")" FINISH_PREFIX')
    def statement(self, p):
        return ('print', p.expr)

    @_('IF condition block')
    def statement(self, p):
        return ('if', p.condition, p.block)

    @_('IF condition block ELSE block')
    def statement(self, p):
        return ('if_else', p.condition, p.block0, p.block1)

    @_('FOR NAME IN expr block')
    def statement(self, p):
        return ('for_loop', p.NAME, p.expr, p.block)

    @_('FUN NAME "(" params ")" block')
    def statement(self, p):
        return ('fun_def', p.NAME, p.params, p.block)

    @_('NAME "(" args ")" FINISH_PREFIX')
    def statement(self, p):
        return ('fun_call', p.NAME, p.args)

    @_('expr FINISH_PREFIX')
    def statement(self, p):
        return p.expr

    @_('expr EQEQ expr')
    def condition(self, p):
        return ('binary', '==', p.expr0, p.expr1)

    @_('expr HIGHEQ expr')
    def condition(self, p):
        return ('binary', '>=', p.expr0, p.expr1)

    @_('expr LOWEQ expr')
    def condition(self, p):
        return ('binary', '<=', p.expr0, p.expr1)

    @_('')
    def params(self, p):
        return []

    @_('NAME')
    def params(self, p):
        return [p.NAME]

    @_('params "," NAME')
    def params(self, p):
        return p.params + [p.NAME]

    @_('')
    def args(self, p):
        return []

    @_('expr')
    def args(self, p):
        return [p.expr]

    @_('args "," expr')
    def args(self, p):
        return p.args + [p.expr]

    @_('expr "+" expr',
       'expr "-" expr',
       'expr "*" expr',
       'expr "/" expr')
    def expr(self, p):
        return ('binary', p[1], p.expr0, p.expr1)

    @_('"-" expr %prec UMINUS')
    def expr(self, p):
        return ('neg', p.expr)

    @_('NAME PLUSEQ expr')
    def expr(self, p):
        return ('aug_assign', p.NAME, '+=', p.expr)

    @_('NAME MINUSEQ expr')
    def expr(self, p):
        return ('aug_assign', p.NAME, '-=', p.expr)

    @_('NAME')
    def expr(self, p):
        return ('var', p.NAME)

    @_('NUMBER')
    def expr(self, p):
        return ('num', p.NUMBER)

    @_('STRING')
    def expr(self, p):
        return ('str', p.STRING)


class HavaExecute:
    def __init__(self, tree, env=None):
        self.env = env or {}
        self.walk_tree(tree)

    def walk_tree(self, ast):
        if ast is None:
            return None
        if isinstance(ast, (int, float, str, bool)):
            return ast
        method = getattr(self, f"visit_{ast[0]}", None)

        if method is None:
            raise RuntimeError(f"Bilinmeyen AST node tipi: {ast[0]}")
        return method(ast)

    def visit_program(self, ast):
        statements = ast[1]
        result = None
        for statement in statements:
            result = self.walk_tree(statement)
        return result

    def visit_block(self, ast):
        result = None
        for statement in ast[1]:
            result = self.walk_tree(statement)
        return result

    def visit_num(self, ast):
        return ast[1]

    def visit_str(self, ast):
        return ast[1]

    def visit_var(self, ast):
        name = ast[1]
        if name not in self.env:
            raise RuntimeError(f"Bilinmeyen değişken: {name}")
        return self.env[name]

    def visit_print(self, ast):
        value = self.walk_tree(ast[1])
        print(value)
        return None

    def visit_assign(self, ast):
        name = ast[1]
        value = self.walk_tree(ast[2])
        self.env[name] = value
        return None

    def visit_aug_assign(self, ast):
        name = ast[1]
        op = ast[2]
        value = self.walk_tree(ast[3])
        if name not in self.env:
            raise RuntimeError(f"Bilinmeyen değişken: {name}")
        if op == '+=':
            self.env[name] += value
        elif op == '-=':
            self.env[name] -= value
        else:
            raise RuntimeError(f"Bilinmeyen atama operatörü: {op}")
        return None

    def visit_binary(self, ast):
        operations = {
            '+': lambda a, b: a + b,
            '-': lambda a, b: a - b,
            '*': lambda a, b: a * b,
            '/': lambda a, b: a / b,
            '==': lambda a, b: a == b,
            '>=': lambda a, b: a >= b,
            '<=': lambda a, b: a <= b,
        }
        op = ast[1]
        left = self.walk_tree(ast[2])
        right = self.walk_tree(ast[3])
        if op not in operations:
            raise RuntimeError(f"Bilinmeyen operatör: {op}")

        return operations[op](left, right)

    def visit_if(self, ast):
        condition = self.walk_tree(ast[1])
        if condition:
            return self.walk_tree(ast[2])
        return None

    def visit_if_else(self, ast):
        condition = self.walk_tree(ast[1])
        if condition:
            return self.walk_tree(ast[2])
        return self.walk_tree(ast[3])

    def visit_fun_def(self, ast):
        name = ast[1]
        params = ast[2]
        body = ast[3]
        self.env[name] = {
            'type': 'function',
            'params': params,
            'body': body,
        }
        return None

    def visit_neg(self, ast):
        return -self.walk_tree(ast[1])

    def visit_for_loop(self, ast):
        name = ast[1]
        limit = self.walk_tree(ast[2])
        body = ast[3]

        old_value = self.env.get(name, None)
        had_old_value = name in self.env

        for i in range(limit):
            self.env[name] = i
            self.walk_tree(body)

        if had_old_value:
            self.env[name] = old_value
        else:
            del self.env[name]

        return None

    def visit_fun_call(self, ast):
        name = ast[1]
        args = ast[2]
        if name not in self.env:
            raise RuntimeError(f"Bilinmeyen fonksiyon: {name}")
        fn = self.env[name]
        if fn.get('type') != 'function':
            raise RuntimeError(f"{name} bir fonksiyon değil")
        params = fn['params']
        body = fn['body']
        if len(params) != len(args):
            raise RuntimeError(
                f"{name} fonksiyonu {len(params)} argüman bekliyor, "
                f"{len(args)} verildi."
            )
        old_env = self.env.copy()
        for param_name, arg_node in zip(params, args):
            self.env[param_name] = self.walk_tree(arg_node)
        result = self.walk_tree(body)
        self.env = old_env
        return result
