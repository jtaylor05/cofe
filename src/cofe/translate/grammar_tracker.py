from cofe.transform.grammar_transform import GrammarWrapper

from pegen.grammar import (
    Grammar,
    NameLeaf
)

class GrammarTracker(GrammarWrapper):
    def __init__(self, grammar: Grammar):
        super().__init__(grammar)
        
        self.reference_table = {}
        
    @property
    def rules(self):
        rules = super().rules
        
        for old, new in self.reference_table:
            if old in rules:
                continue
            if new not in rules:
                continue
            rules[old] = rules[new]
        
        return rules
        
    def set_type_name(self, type, value, new_value):
        _store_ref = type is NameLeaf

        super().set_type_name(type, value, new_value)
        
        if _store_ref:
            self.reference_table[value] = new_value