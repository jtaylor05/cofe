import io
from typing import Dict, Any, Type

from pegen.grammar import Grammar
from pegen.grammar_parser import GeneratedParser as GrammarParser
from pegen.parser import Parser
from pegen.python_generator import PythonParserGenerator
from pegen.utils import parse_string

def get_python_grammar() -> Grammar:
    """Returns the base Python grammar as a Grammar object. Base Grammar is loaded from pegen's python.gram file."""
    with open("python.gram", 'r') as gf:
        src = gf.read()
        grammar = parse_string(src, GrammarParser)
    return grammar

def generate_ython_parser(grammar: Grammar, path: str = None) -> Type[Parser]:
    out = io.StringIO()
    genr = PythonParserGenerator(grammar, out)
    genr.generate("<string>")
    
    ns: Dict[str, Any] = {}
    
    exec(out.getvalue(), ns)
    class_name = grammar.metas.get("class", "PythonParser")
    return ns[class_name]
    

# def generate_parser(
#     grammar: Grammar, parser_path: Optional[str] = None, parser_name: str = "GeneratedParser"
# ) -> Type[Parser]:
#     # Generate a parser.
#     out = io.StringIO()
#     genr = PythonParserGenerator(grammar, out)
#     genr.generate("<string>")

#     # Load the generated parser class.
#     ns: Dict[str, Any] = {}
#     if parser_path:
#         with open(parser_path, "w") as f:
#             f.write(out.getvalue())
#         mod = import_file("py_parser", parser_path)
#         return getattr(mod, parser_name)
#     else:
#         exec(out.getvalue(), ns)
#         return ns[parser_name]