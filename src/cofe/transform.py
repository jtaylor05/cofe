import ast

from .grammar_transform import GrammarWrapper

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
   