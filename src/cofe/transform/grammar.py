from cofe.transform.grammar_transform import GrammarWrapper
from cofe.transform.transformer import Transform
from cofe.utils import get_python_grammar

class PythonGrammar:
    def __init__(self):
        self._modifications: list[Transform] = []
        self._grammar = None
        
    def apply_modifications(self):
        self._grammar = GrammarWrapper(get_python_grammar())
        
        for mod in self._modifications:
            mod.apply_grammar(self._grammar)
    
    def add_modification(self, modification: Transform | list[Transform]):
        if not isinstance(modification, list): modification = [modification]
        self._modifications.extend(modification)
        self._grammar = None  # Invalidate the cached grammar
    
    @property
    def grammar(self) -> GrammarWrapper:
        if self._grammar is None:
            self.apply_modifications()
        return self._grammar
    
class CustomUnparser:
    def unparse(self, node) -> str:
        pass