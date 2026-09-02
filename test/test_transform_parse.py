import pytest, ast
from pegen.grammar import NameLeaf, StringLeaf
from pegen.grammar_parser import GeneratedParser as GrammarParser
from pegen.utils import parse_string
from cofe import (
    GrammarWrapper,
    InjectAlt,
    RenameLeaf,
    RenameRule,
    ReplaceRuleBody,
    StrictCallTransformer,
    StrictFuncDefTransformer,
    StrictImportTransformer,
    StrictImportFromTransformer,
    AggregateTransformer,
    AggregateFuncTransformer,
    AggregateImportTransformer,
    get_python_grammar,
    generate_ython_parser
)

def make_wrapper(source: str) -> GrammarWrapper:
    grammar = parse_string(source, GrammarParser)
    return GrammarWrapper(grammar)

def test_plus_transform():
    wrapper = GrammarWrapper(get_python_grammar())
    
    wrapper.set_type_name(StringLeaf, "'+'", "'PLUS'")
    
    parser_cls = generate_ython_parser(wrapper.grammar)
    
    src = """a PLUS b"""
    
    node = parse_string(src, parser_cls)
    
    print(ast.unparse(node))
    
test_plus_transform()
    
    
