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
    
    RenameLeaf(StringLeaf, "'+'", "'PLUS'").apply(wrapper)
    
    parser_cls = generate_ython_parser(wrapper.grammar)
    
    src = """def add(a, b):
    return a PLUS b
assert add(2, 3) == 2 PLUS 3"""
    
    node = parse_string(src, parser_cls)
    
    trans = AggregateFuncTransformer("add", "sum")
    trans.visit(node)
    
    print(ast.unparse(node))
    
def test_when_transform():
    wrapper = GrammarWrapper(get_python_grammar())
    
    print(wrapper)
    
    ReplaceRuleBody("if_stmt", """if_stmt[ast.If]:
    | invalid_if_stmt
    | 'if' '(' a=named_expression ')' ':' b=block c=elif_stmt { ast.If(test=a, body=b, orelse=c or [], LOCATIONS) }
    | 'if' '(' a=named_expression ')' ':' b=block c=[else_block] { ast.If(test=a, body=b, orelse=c or [], LOCATIONS) }""").apply(wrapper)
    
    InjectAlt("invalid_if_stmt", """'if' named_expression { self.raise_syntax_error("expected '('") }""", True).apply(wrapper)
    InjectAlt("invalid_if_stmt", """'if' '(' named_expression { self.raise_syntax_error("expected ')'") }""", True).apply(wrapper)
    
    #print(wrapper)
    
    RenameLeaf(StringLeaf, "'if'", "'when'").apply(wrapper)
    
    #print(wrapper)
    
    parser_cls = generate_ython_parser(wrapper.grammar)
    
    src = """
when (x > 0):
    return True"""
    
    node = parse_string(src, parser_cls)
    
    print(ast.unparse(node))
    
test_when_transform()
