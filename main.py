from hava.compiler import HavaCompiler
from hava.parser import HavaParser, HavaLexer
from hava.vm import HavaVM

lexer = HavaLexer()
parser = HavaParser()
vm = HavaVM()

while True:
    source = input("Hava > ")
    tree = parser.parse(lexer.tokenize(source))
    print(tree)
    compiler = HavaCompiler()
    bytecode = compiler.compile(tree)
    vm.run(bytecode)
