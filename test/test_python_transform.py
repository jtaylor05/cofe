import ast

import pytest
from pegen.grammar import StringLeaf
from pegen.grammar_parser import GeneratedParser as GrammarParser
from pegen.utils import parse_string

from cofe.transform.ast_transform import AggregateFuncTransformer
from cofe.transform.grammar_transform import (
    GrammarWrapper,
    InjectAlt,
    RenameLeaf,
    ReplaceRuleBody,
)
from cofe.utils import generate_ython_parser, get_python_grammar


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
    transform = AggregateFuncTransformer("add", "sum")
    transform.visit(node)

    assert "sum" in ast.unparse(node)


def test_when_transform():
    wrapper = GrammarWrapper(get_python_grammar())

    ReplaceRuleBody(
        "if_stmt",
        """if_stmt[ast.If]:
    | invalid_if_stmt
    | 'if' '(' a=named_expression ')' ':' b=block c=elif_stmt { ast.If(test=a, body=b, orelse=c or [], LOCATIONS) }
    | 'if' '(' a=named_expression ')' ':' b=block c=[else_block] { ast.If(test=a, body=b, orelse=c or [], LOCATIONS) }""",
    ).apply(wrapper)

    InjectAlt(
        "invalid_if_stmt",
        """'if' named_expression { self.raise_syntax_error("expected '('") }""",
        prepend=True,
    ).apply(wrapper)
    InjectAlt(
        "invalid_if_stmt",
        """'if' '(' named_expression { self.raise_syntax_error("expected ')'") }""",
        prepend=True,
    ).apply(wrapper)

    RenameLeaf(StringLeaf, "'if'", "'when'").apply(wrapper)

    parser_cls = generate_ython_parser(wrapper.grammar)

    src = """
when (x > 0):
    return True"""

    node = parse_string(src, parser_cls)
    assert ast.unparse(node)

