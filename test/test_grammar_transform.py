import pytest
from pegen.grammar import NameLeaf, StringLeaf
from pegen.grammar_parser import GeneratedParser as GrammarParser
from pegen.utils import parse_string
from cofe import (
    GrammarWrapper,
    InjectAlt,
    RenameLeaf,
    RenameRule,
    ReplaceRuleBody,
)


def make_wrapper(source: str) -> GrammarWrapper:
    grammar = parse_string(source, GrammarParser)
    return GrammarWrapper(grammar)


def test_rename_leaf():
    wrapper = make_wrapper("sum: sum '+' term | term\n")

    RenameLeaf(StringLeaf, "'+'", "'@'").apply(wrapper)
    
    print(wrapper)

    assert (StringLeaf, "'@'") in wrapper.names
    assert (StringLeaf, "'+'") not in wrapper.names


def test_rename_leaf_missing_leaf():
    wrapper = make_wrapper("sum: term\n")

    with pytest.raises(ValueError):
        RenameLeaf(NameLeaf, "missing", "expr").apply(wrapper)


def test_rename_rule():
    wrapper = make_wrapper("start: expr\nexpr: NUMBER\n")

    RenameRule("expr", "term").apply(wrapper)

    assert "term" in wrapper.rules
    assert "expr" not in wrapper.rules
    assert (NameLeaf, "term") in wrapper.names


def test_rename_rule_missing_rule():
    wrapper = make_wrapper("start: expr\n")

    with pytest.raises(KeyError):
        RenameRule("missing", "term").apply(wrapper)


def test_replace_rule_body():
    wrapper = make_wrapper("sum: NUMBER\n")

    ReplaceRuleBody("sum", "sum: NUMBER '+' NUMBER").apply(wrapper)

    assert "'+'" in str(wrapper.rules["sum"].rhs)


def test_replace_rule_body_wrong_rule():
    wrapper = make_wrapper("sum: NUMBER\n")

    with pytest.raises(ValueError):
        ReplaceRuleBody("sum", "term: NUMBER").apply(wrapper)


def test_inject_alt():
    wrapper = make_wrapper("expr: NUMBER\n")
    original_count = len(wrapper.rules["expr"].rhs.alts)

    InjectAlt("expr", "'(' expr ')'", prepend=True).apply(wrapper)

    alternatives = wrapper.rules["expr"].rhs.alts
    assert len(alternatives) == original_count + 1
    assert "'('" in str(alternatives[0])


def test_inject_alt_missing_rule():
    wrapper = make_wrapper("expr: NUMBER\n")

    with pytest.raises(KeyError):
        InjectAlt("missing", "NUMBER").apply(wrapper)
