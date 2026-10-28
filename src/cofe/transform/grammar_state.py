from __future__ import annotations

from typing import Dict, List, Tuple, Type, Optional
from typing import Union

from cofe.utils import get_python_grammar
from cofe.transform.grammar_transform import gather_names

from pegen.grammar import (
    Grammar,
    Leaf,
    Rule,
    Rhs,
    NameLeaf,
    StringLeaf
)

NameTable = Dict[Tuple[Type, str], List[Leaf]]

# mapping from rule-name to base CofeRule class
_SPECIAL_BASE_CLASSES = {
    
}

class PythonGrammarState(Grammar):
    def __init__(self, grammar: Optional[Grammar] = None):
        self.rules = {k: (_SPECIAL_BASE_CLASSES[k](r) if k in _SPECIAL_BASE_CLASSES else CofeRule(r)) for k, r in grammar.rules.items()}
        self.metas = dict(grammar.metas)
        self.names: NameTable = gather_names(self)
    
    def regather_names(self):
        self.names = gather_names(self)
    
    def set_leaf_name(self, type: Union[Type[NameLeaf], Type[StringLeaf]], value: str, new_value:str):
        key, new_key = (type, value), (type, new_value)
        if key not in self.names:
            raise ValueError(f"Leaves of type {type} and value {value} not in nametable.")
        if new_key in self.names:
            raise ValueError(f"Leaves of type {type} and value {new_value} already in nametable.")
        
        for node in self.names[key]:
            node.value = new_value
        
        self.names[new_key] = self.names.pop(key)

class CofeRule(Rule):
    def __init__(self, rule: Rule):
        super().__init__(rule.name, rule.type, rule.rhs, rule.memo)

    def unparse(self) -> str:
        return str(self)
    
class IfStmtRule(CofeRule):
    def __init__(self, rule: Rule):
        super().__init__(rule)
        
        self._stmt_str = 'if'
        self._sep_str  = ':'
        
# ['when:', named_expression, block, elif_stmt]
# ['if', ]
    
class PythonGrammarPrior:
    def __init__(self):
        pass