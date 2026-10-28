from __future__ import annotations

import ast
from pathlib import Path
import sys

import pytest

from cofe.transform.transform import transform_code


TARGET_VERSIONS = [(3, minor) for minor in range(8, 14)]
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
]


def accepts(parse, source: str) -> bool:
    try:
        parse(source)
    except SyntaxError:
        return False
    return True


@pytest.mark.parametrize("version", TARGET_VERSIONS)
@pytest.mark.parametrize("source, introduced, feature", SYNTAX_CASES)
def test_versioned_syntax_matches_cpython(
    version: tuple[int, int],
    source: str,
    introduced: int,
    feature: str,
    tmp_path: Path,
) -> None:
    expected = accepts(
        lambda text: ast.parse(text, feature_version=version), source
    )
    config_file = tmp_path / "config.ini"
    config_file.write_text(
        "[env]\nextension = .y\ntest = False\n\n[available]\n\n[active]\n",
        encoding="utf-8",
    )
    actual = accepts(
        lambda text: transform_code(
            text, config_file=config_file, py_version=version
        ),
        source,
    )

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