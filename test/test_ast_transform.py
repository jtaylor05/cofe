import ast
import pytest
from ython import (
    StrictCallTransformer,
    StrictFuncDefTransformer,
    StrictImportTransformer,
    StrictImportFromTransformer,
    AggregateTransformer,
    AggregateFuncTransformer,
    AggregateImportTransformer
)

def test_call_transformer():
    src="""foo(2, 3)"""
    ans="""bar(2, 3)"""
    
    root = ast.parse(src)
    
    trans = StrictCallTransformer("foo", "bar")
    trans.visit(root)
    
    checked = ast.unparse(root)
    assert ans == checked


def test_call_transformer_collision():
    root = ast.parse("bar(2, 3)")
    trans = StrictCallTransformer("foo", "bar")

    with pytest.raises(NameError):
        trans.visit(root)


def test_func_def_transformer():
    src = """
def foo(a: int, b):
    return a+b
    """
    ans = "def bar(a: int, b):\n    return a + b"
    root = ast.parse(src)

    trans = StrictFuncDefTransformer("foo", "bar")
    trans.visit(root)

    checked = ast.unparse(root)
    assert ans == checked


def test_func_def_transformer_collision():
    root = ast.parse("def bar():\n    pass")
    trans = StrictFuncDefTransformer("foo", "bar")

    with pytest.raises(NameError):
        trans.visit(root)


def test_import_transformer():
    root = ast.parse("import foo")
    trans = StrictImportTransformer("foo", "bar")
    trans.visit(root)

    assert ast.unparse(root) == "import bar as foo"


def test_import_transformer_collision():
    root = ast.parse("import bar")
    trans = StrictImportTransformer("foo", "bar")

    with pytest.raises(NameError):
        trans.visit(root)


def test_import_from_transformer():
    root = ast.parse("from foo import value")
    trans = StrictImportFromTransformer("foo", "bar")
    trans.visit(root)

    assert ast.unparse(root) == "from bar import value"


def test_import_from_transformer_collision():
    root = ast.parse("from bar import value")
    trans = StrictImportFromTransformer("foo", "bar")

    with pytest.raises(NameError):
        trans.visit(root)


def test_aggregate_transformer():
    src = """
def foo():
    return foo()
    """
    ans = "def bar():\n    return bar()"
    root = ast.parse(src)

    trans = AggregateTransformer(
        StrictCallTransformer("foo", "bar"),
        StrictFuncDefTransformer("foo", "bar"),
    )
    trans.visit(root)
    
    #print(ast.dump(root, indent=2))

    checked = ast.unparse(root)
    assert ans == checked


def test_aggregate_transformer_collision():
    root = ast.parse("bar()")
    trans = AggregateTransformer(StrictCallTransformer("foo", "bar"))

    with pytest.raises(NameError):
        trans.visit(root)


def test_aggregate_func_transformer():
    src = """
def foo():
    return foo()
    """
    ans = "def bar():\n    return bar()"
    root = ast.parse(src)

    trans = AggregateFuncTransformer("foo", "bar")
    trans.visit(root)

    checked = ast.unparse(root)
    assert ans == checked


def test_aggregate_func_transformer_collision():
    root = ast.parse("def bar():\n    pass")
    trans = AggregateFuncTransformer("foo", "bar")

    with pytest.raises(NameError):
        trans.visit(root)


def test_aggregate_import_transformer():
    src = """
import foo
from foo import value
    """
    ans = "import bar as foo\nfrom bar import value"
    root = ast.parse(src)

    trans = AggregateImportTransformer("foo", "bar")
    trans.visit(root)

    checked = ast.unparse(root)
    assert ans == checked


def test_aggregate_import_transformer_collision():
    root = ast.parse("import bar")
    trans = AggregateImportTransformer("foo", "bar")

    with pytest.raises(NameError):
        trans.visit(root)
    
