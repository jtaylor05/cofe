import io, ast, sys
import inspect
from typing import Dict, Any, Type

from pathlib import Path
from importlib import import_module, util

from pegen.grammar import Grammar
from pegen.grammar_parser import GeneratedParser as GrammarParser
from pegen.parser import Parser
from pegen.python_generator import PythonParserGenerator
from pegen.utils import parse_string

from .configure import matches_transform

type ASTRoot = ast.AST
type PathLike = str | Path
type TransformMatches = list[tuple[type[object], Path]]

def get_python_grammar() -> Grammar:
    """Returns the base Python grammar as a Grammar object. Base Grammar is loaded from pegen's python.gram file."""
    with open(Path(__file__).parent/"python.gram", 'r') as gf:
        src = gf.read()
        grammar = parse_string(src, GrammarParser)
    return grammar

def generate_ython_parser(grammar: Grammar) -> Type[Parser]:
    out = io.StringIO()
    genr = PythonParserGenerator(grammar, out)
    genr.generate("<string>")
    
    ns: Dict[str, Any] = {}
    
    exec(out.getvalue(), ns)
    class_name = grammar.metas.get("class", "PythonParser")
    return ns[class_name]

def parse_from_grammar(src: str, grammar: Grammar) -> ASTRoot:
    prs = generate_ython_parser(grammar)
    
    return parse_string(src, prs)

#==================================================================================#

def import_module_from_file(module_name: str, file_path: PathLike):
    spec = util.spec_from_file_location(module_name, file_path)
    
    module = util.module_from_spec(spec)
    
    sys.modules[module_name] = module
    
    spec.loader.exec_module(module)
    
    return module

def get_transformers(fp: PathLike, extension: str=".py") -> TransformMatches:
    fp = Path(fp).resolve()
    if not fp.is_file():
        raise ValueError(f"Input file {fp} is not a file.")
    if not fp.suffix == extension:
        return []
    
    try:
        module = import_module_from_file(fp.name, str(fp))

        return [(cls, fp) for _, cls in inspect.getmembers(module, inspect.isclass) if inspect.getmodule(cls) == module and matches_transform(cls)]
    except:
        return []

def gather_transformers(root: PathLike, depth: int=5, extension: str=".py") -> TransformMatches:
    """Gathers all transformers recursively appearing in python files ending with 'extension', including root.
    Guarantees that the returned objects match the Transform members, but not neccessarily that they are Transform subclasses.
    
    Returns an array of tuples, with the first element of each tuple being the class and the second being its file path."""
    root = Path(root).resolve()
    if not root.exists():
        raise ValueError(f"Path {root} does not exist.")
    
    if depth == 0:
        return []
    
    if root.is_file():
        return get_transformers(root, extension=extension)
    
    ret = []
    for child in root.iterdir():
        if child.is_file():
            ret += get_transformers(child, extension=extension)
        else:
            gather_transformers(child, depth=depth-1)
    return ret