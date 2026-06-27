from .sly import Parser
from .sly import Lexer
from .errors import HavaLexerError, find_column, HavaParserError

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

    "dondur": "RETURN",
    "döndür": "RETURN",
    "return": "RETURN",
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
    ignore = "\t "
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

    def __init__(self):
        self.source = ""

    @_(r"\n+")
    def ignore_newline(self, t):
        self.lineno += t.value.count("\n")

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
        column = find_column(self.source, t)
        raise HavaLexerError(
            f"Geçersiz karakter: {t.value[0]!r}",
            line=self.lineno,
            column=column,
            source=self.source,
        )


class HavaParser(Parser):
    tokens = HavaLexer.tokens
    start = 'program'

    precedence = (
        ('nonassoc', 'EQEQ', 'HIGHEQ', 'LOWEQ'),
        ('left', '+', '-'),
        ('left', '*', '/'),
        ('right', 'UMINUS'),
    )

    def __init__(self):
        self.source = ""

    def error(self, p):
        if p is None:
            raise HavaParserError("Beklenmeyen dosya sonu", source=self.source)

        column = find_column(self.source, p)

        raise HavaParserError(
            f"Beklenmeyen token: {p.type} ({p.value!r})",
            line=p.lineno,
            column=column,
            source=self.source,
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

    @_('IF expr block')
    def statement(self, p):
        return ('if', p.expr, p.block)

    @_('IF expr block ELSE block')
    def statement(self, p):
        return ('if_else', p.expr, p.block0, p.block1)

    @_('FOR NAME IN expr block')
    def statement(self, p):
        return ('for_loop', p.NAME, p.expr, p.block)

    @_('FUN NAME "(" params ")" block')
    def statement(self, p):
        return ('fun_def', p.NAME, p.params, p.block)

    @_('RETURN expr FINISH_PREFIX')
    def statement(self, p):
        return ('return', p.expr)

    @_('expr FINISH_PREFIX')
    def statement(self, p):
        return ('expr_stmt', p.expr)

    @_('expr EQEQ expr',
       'expr HIGHEQ expr',
       'expr LOWEQ expr')
    def expr(self, p):
        return ('binary', p[1], p.expr0, p.expr1)

    @_('"(" expr ")"')
    def expr(self, p):
        return p.expr

    @_('')
    def params(self, p):
        return []

    @_('param_list')
    def params(self, p):
        return p.param_list

    @_('NAME')
    def param_list(self, p):
        return [p.NAME]

    @_('param_list "," NAME')
    def param_list(self, p):
        return p.param_list + [p.NAME]

    @_('')
    def args(self, p):
        return []

    @_('arg_list')
    def args(self, p):
        return p.arg_list

    @_('expr')
    def arg_list(self, p):
        return [p.expr]

    @_('arg_list "," expr')
    def arg_list(self, p):
        return p.arg_list + [p.expr]

    @_('expr "+" expr',
       'expr "-" expr',
       'expr "*" expr',
       'expr "/" expr')
    def expr(self, p):
        return ('binary', p[1], p.expr0, p.expr1)

    @_('"-" expr %prec UMINUS')
    def expr(self, p):
        return ('neg', p.expr)

    @_('NAME PLUSEQ expr FINISH_PREFIX')
    def statement(self, p):
        return ('aug_assign', p.NAME, '+=', p.expr)

    @_('NAME MINUSEQ expr FINISH_PREFIX')
    def statement(self, p):
        return ('aug_assign', p.NAME, '-=', p.expr)

    @_('NAME "(" args ")"')
    def expr(self, p):
        return ('fun_call', p.NAME, p.args)

    @_('NAME')
    def expr(self, p):
        return ('var', p.NAME)

    @_('NUMBER')
    def expr(self, p):
        return ('num', p.NUMBER)

    @_('STRING')
    def expr(self, p):
        return ('str', p.STRING)
