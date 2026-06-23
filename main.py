import argparse
from pathlib import Path

from hava.compiler import HavaCompiler
from hava.errors import HavaError
from hava.parser import HavaParser, HavaLexer
from hava.vm import HavaVM

lexer = HavaLexer()
parser = HavaParser()
vm = HavaVM()
cli_args_init = argparse.ArgumentParser()
cli_args_init.add_argument("--file", help="Path to a .hava file to run.", type=str)
cli_args_init.add_argument("--ast", help="Print generated AST.", action="store_true")
cli_args = cli_args_init.parse_args()


def process_tree(source):
    lexer.source = source
    parser.source = source
    tree = parser.parse(lexer.tokenize(source))
    if cli_args.ast:
        print(tree)
    compiler = HavaCompiler()
    bytecode = compiler.compile(tree)

    vm.run(bytecode)

def hava_reader():
    source = Path(cli_args.file).read_text(encoding="utf-8")
    process_tree(source)

def hava_repl():
    while True:
        try:
            repl_command = input("Hava REPL > ")
            if not repl_command:
                continue
            if repl_command in ("exit", "quit", "çık"):
                break
            process_tree(repl_command)
        except KeyboardInterrupt:
            print("\nExiting.")
            break
        except EOFError:
            print("\nExiting.")
            break
        except HavaError as e:
            print(e)
        except Exception as e:
            print(f"Internal error: {e}")

if __name__ == "__main__":
    if cli_args.file:
        hava_reader()
    else:
        hava_repl()

