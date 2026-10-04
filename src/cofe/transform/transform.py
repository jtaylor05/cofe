from typing import Any, Callable
import ast, sys
import warnings

from .grammar_transform import GrammarWrapper
from ..config.configure import PackageConfigParser

from pathlib import Path
from abc import ABC

type AST = ast.AST

def matches_transform(cls: type):
    properties_transform = { attr for attr in dir(Transform) }
    properties_cls = { attr for attr in dir(cls) }
    
    return properties_transform.issubset(properties_cls)

class Transform:
        
    def apply_grammar(self, grammar : GrammarWrapper):
        pass
    
    def apply_ast(self, root : ast.AST):
        pass
    
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

def call_method_safe(obj, method_name, *args, type=None, **kwargs):
    if hasattr(obj, method_name):
        if type:
            return type(getattr(obj, method_name)(args, kwargs))
        else:
            return getattr(obj, method_name)(args, kwargs)
    return None

def _method_unimplemented_factory(method_name: str = None) -> Callable[..., Any]:
    def method_unimplemented():
        raise NotImplementedError(f"Method {method_name} is not implemented. Please implement this method in this class.")
    return method_unimplemented

class Transformation(ABC):
    
    preprocess: Callable[[str], str]     = _method_unimplemented_factory("preprocess")
    modify_grammar: Callable[[Any], Any] = _method_unimplemented_factory("modify_grammar")
    modify_ast: Callable[[AST], AST]     = _method_unimplemented_factory("modify_ast")
    postprocess: Callable[[str], str]    = _method_unimplemented_factory("postprocess")
    
    def __init_subclass__(cls):
        super().__init_subclass__()
        
        module_name = cls.__module__
        module = sys.modules.get(module_name)
        
        if module and hasattr(module, "__file__"):
            file = Path(module.__file__).resolve()
            conf = PackageConfigParser()
            conf.add_transformer(cls.__name__, file)
            conf.write()
        else:
            warnings.warn(f"Cannot find filepath to class {cls.__name__}. Ignoring.")
        