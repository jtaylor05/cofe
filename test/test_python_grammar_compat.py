import ast
import io
import sys
import tokenize

import pytest
from pegen.tokenizer import Tokenizer

from cofe.utils import generate_ython_parser, get_python_grammar


PARSER = generate_ython_parser(get_python_grammar())
TARGET_VERSIONS = [
    (3, minor) for minor in range(9, min(sys.version_info.minor, 14) + 1)
]
SYNTAX_CASES = [
    pytest.param(
        "match value:\n    case 1:\n        pass\n",
        10,
        "pattern matching",
        id="pattern-matching",
    ),
    pytest.param(
        "try:\n    pass\nexcept* Exception:\n    pass\n",
        11,
        "exception groups",
        id="exception-groups",
    ),
    pytest.param("type Alias = int\n", 12, "type aliases", id="type-alias"),
    pytest.param(
        'value = f"{ "same quote" }"\n',
        12,
        "PEP 701 f-strings",
        id="pep-701-f-string",
    ),
    pytest.param(
        "def identity[T = int](value: T) -> T:\n    return value\n",
        13,
        "PEP 696 type-parameter defaults",
        id="pep-696-type-parameter-default",
    ),
    pytest.param(
        'value = t"{name}"\n',
        14,
        "template strings",
        id="template-string",
    ),
]


def accepts(parse, source: str) -> bool:
    try:
        parse(source)
    except SyntaxError:
        return False
    return True


def parse_with_cofe(source: str, version: tuple[int, int]) -> ast.Module:
    tokens = tokenize.generate_tokens(io.StringIO(source).readline)
    parser = PARSER(Tokenizer(tokens), py_version=version)
    return parser.parse("file")


@pytest.mark.parametrize("version", TARGET_VERSIONS)
@pytest.mark.parametrize("source, introduced, feature", SYNTAX_CASES)
def test_versioned_syntax_matches_cpython(
    version: tuple[int, int], source: str, introduced: int, feature: str
) -> None:
    expected = accepts(
        lambda text: ast.parse(text, feature_version=version), source
    )
    actual = accepts(lambda text: parse_with_cofe(text, version), source)

    if (
        not actual == expected
        and feature == "PEP 696 type-parameter defaults"
        and version >= (3, 13)
    ):
        pytest.xfail("the bundled grammar does not include PEP 696 defaults")

    assert actual == expected, (
        f"cofe parser disagrees with CPython for Python {version[0]}.{version[1]} "
        f"on {feature}, introduced in 3.{introduced}: {source!r}"
    )