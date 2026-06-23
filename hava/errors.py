class HavaError(Exception):
    def __init__(self, message, line=None, column=None, source=None):
        self.message = message
        self.line = line
        self.column = column
        self.source = source
        super().__init__(message)

    def __str__(self):
        if self.line is None or self.column is None or self.source is None:
            return self.message
        lines = self.source.splitlines()
        if self.line - 1 < 0 or self.line - 1 >= len(lines):
            return self.message
        source_line = lines[self.line - 1]
        return (
            f"{self.message}\n"
            f"line {self.line}, column {self.column}\n"
            f"{source_line}\n"
            f"{' ' * (self.column - 1)}^"
        )


class HavaLexerError(HavaError):
    pass


class HavaParserError(HavaError):
    pass


class HavaCompilerError(HavaError):
    pass


class HavaRuntimeError(HavaError):
    pass


def find_column(source, token):
    last_newline = source.rfind("\n", 0, token.index)

    if last_newline < 0:
        return token.index + 1

    return token.index - last_newline
