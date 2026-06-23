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

    literals = {
        "+", "-", "*", "/",
        "(", ")", ","
    }

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
