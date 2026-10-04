import ast
import types
from typing import Type

from dataclasses import dataclass

from pegen.grammar import Grammar

type ASTNode = ast.AST
type PropertyName = str

class ASTTransformer(ast.NodeTransformer):
    def __init__(self, type):
        self.type = type
        setattr(self, self.func_name, self.func_wrapper)
    
    @property
    def func_name(self):
        return "visit_" + self.type.__name__
    
    @property
    def func_wrapper(self):
        return self.generic_visit_wrapper(self.apply)
    
    def generic_visit_wrapper(self, func):
        def wrapper(node: ASTNode) -> ASTNode:
            node = func(node)
            self.generic_visit(node)
            return node
        return wrapper
    
    def apply(self, node: ASTNode) -> ASTNode:
        raise NotImplementedError()

class StrictCallTransformer(ASTTransformer):    
    def __init__(self, old: str, new: str):
        super().__init__(ast.Call)
        self.old = old
        self.new = new
    
    def apply(self, node: ASTNode) -> ASTNode:
        if not isinstance(node, ast.Call):
            return node
        if isinstance(node.func, ast.Name):
            if node.func.id == self.old:
                node.func.id = self.new
            elif node.func.id == self.new:
                raise NameError(f"Cannot call name {self.new} as function name. Collides during transformation. Try {self.old} instead.")
        if isinstance(node.func, ast.Attribute) and node.func.attr == self.old:
            if node.func.attr == self.old:
                node.func.attr = self.new
            elif node.func.attr == self.new:
                raise NameError(f"Cannot call name '{self.new}' as function name. Collides during transformation. Try {self.old} instead.")
        return node

class StrictFuncDefTransformer(ASTTransformer):
    def __init__(self, old: str, new: str):
        super().__init__(ast.FunctionDef)
        self.old = old
        self.new = new
    
    def apply(self, node: ASTNode) -> ASTNode:
        if not isinstance(node, ast.FunctionDef):
            return node
        if node.name == self.old:
            node.name = self.new
        elif node.name == self.new:
            raise NameError(f"Cannot define function name '{self.new}'. Collides during transformation. Try {self.old} instead.")
        return node

class StrictImportTransformer(ASTTransformer):
    def __init__(self, old: str, new: str):
        super().__init__(ast.Import)
        self.old = old
        self.new = new
    
    def apply(self, node: ASTNode) -> ASTNode:
        if not isinstance(node, ast.Import):
            return node
        for n in node.names:
            if n.name == self.old:
                n.name = self.new
                n.asname = self.old
            elif n.name == self.new:
                raise NameError(f"Cannot import '{n.name}' because it conflicts on transformation. Try {self.old} instead.")
        return node

class StrictImportFromTransformer(ASTTransformer):
    def __init__(self, old: str, new: str):
        super().__init__(ast.ImportFrom)
        self.old = old
        self.new = new
        
    def apply(self, node: ASTNode) -> ASTNode:
        if not isinstance(node, ast.ImportFrom):
            return node
        if node.module == self.old:
            node.module = self.new
        elif node.module == self.new:
            raise NameError(f"Cannot import from '{node.module}' beacuse it conflicts on transformation. Try {self.old} instead.")
        return node
  
    
class AggregateTransformer(ast.NodeTransformer):
    def __init__(self, *args: ASTTransformer):
        dp = {}
        for t in args:
            dp.setdefault(t.func_name, []).append(t)
        
        for func_name in dp:
            setattr(self, func_name, self.aggregate_wrapper(dp[func_name]))
        
    def aggregate_wrapper(self, transformers: list[ASTTransformer]):
        def wrapper(node: ASTNode) -> ASTNode:
            for t in transformers:
                node = t.apply(node)
            self.generic_visit(node)
            return node
        return wrapper
    
    
class AggregateFuncTransformer(AggregateTransformer):
    def __init__(self, old: str, new: str):
        super().__init__(StrictCallTransformer(old, new), StrictFuncDefTransformer(old, new))

class AggregateImportTransformer(AggregateTransformer):
    def __init__(self, old: str, new: str):
        super().__init__(StrictImportTransformer(old, new), StrictImportFromTransformer(old, new))
    
if __name__=="__main__":
    src = """
def foo(a, b):
    return foo(a-1, b)
    """
    
    src_error = """
def foo(a, b):
    return a+b

def bar(a, b):
    return a-b

bar(2, 1) 
print(foo(1, 2))
    """
    root = ast.parse(src)
    
    trans = AggregateFuncTransformer("foo", "bar")
    
    trans.visit(root)
    
    #print(ast.dump(root, indent=2))
    print(ast.unparse(root))
    