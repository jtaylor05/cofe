from typing import Any, Callable
import ast
import sys
import functools
import warnings

from cofe.transform.grammar_transform import GrammarWrapper
from cofe.config.configure import PackageConfigParser
from cofe.utils import import_module_from_file, get_python_grammar, parse_from_grammar

from pathlib import Path
from abc import ABC

type PathLike = str | Path
type AST = ast.AST

def matches_transform(cls: type):
    properties_transform = { attr for attr in dir(Transform) }
    properties_cls = { attr for attr in dir(cls) }
    
    return properties_transform.issubset(properties_cls)

class Transform:
    
    def preprocess(self, source: str) -> str:
        return source
    
    def apply_grammar(self, grammar : GrammarWrapper):
        pass
    
    def apply_ast(self, root : ast.AST):
        pass
    
    def postprocess(self, source: str) -> str:
        return source
    
    def get_sort(self):
        return 0
        
    def __lt__(self, other):
        if not isinstance(other, Transform):
            raise NotImplementedError("Can only compare with other Transform subclasses.")
        return self.get_sort() < other.get_sort()
    
    def __le__(self, other):
        if not isinstance(other, Transform):
            raise NotImplementedError("Can only compare with other Transform subclasses.")
        return self.get_sort() <= other.get_sort()
    
    def __eq__(self, other):
        if not isinstance(other, Transform):
            raise NotImplementedError("Can only compare with other Transform subclasses.")
        return self.get_sort() == other.get_sort()
    
    def __ne__(self, other):
        if not isinstance(other, Transform):
            raise NotImplementedError("Can only compare with other Transform subclasses.")
        return self.get_sort() != other.get_sort()
    
    def __ge__(self, other):
        if not isinstance(other, Transform):
            raise NotImplementedError("Can only compare with other Transform subclasses.")
        return self.get_sort() >= other.get_sort()
    
    def __gt__(self, other):
        if not isinstance(other, Transform):
            raise NotImplementedError("Can only compare with other Transform subclasses.")
        return self.get_sort() > other.get_sort()
    
    def __hash__(self):
        return object.__hash__(self)
    
@functools.cache
def get_transformer_src(file_path: PathLike = None):
    config = PackageConfigParser(config_file=file_path)
    
    _modules = {}
            
    transformers: list[Transform] = []
    
    for cls, f in config.get_active().items():
        p = Path(f)
        module_name = p.name
        
        if module_name in _modules:
            class_var = getattr(_modules[module_name], cls)
            if matches_transform(class_var):
                transformers.append(class_var())
            continue
        
        module = import_module_from_file(module_name, p)
        
        _modules[module_name] = module
        class_var = getattr(module, cls)
        if matches_transform(class_var):
            transformers.append(class_var())
    
    transformers.sort(key=lambda t: t.get_sort())
    return transformers

def transform_code(source: str, config_file: PathLike = None) -> str:
    grammar = GrammarWrapper(get_python_grammar())
    
    transformers = get_transformer_src(file_path=config_file)
    
    for t in transformers:
        source = t.preprocess(source)
    
    for t in transformers:
        t.apply_grammar(grammar)
    
    root = None
    try:
        root = parse_from_grammar(source, grammar)
    except Exception as e:
        raise e
    
    for t in transformers:
        t.apply_ast(root)
        
    transformed = ast.unparse(root)
    
    for t in transformers:
        transformed = t.postprocess(transformed)

    return transformed
        