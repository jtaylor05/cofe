from cofe.configure import Transform
from cofe import RenameLeaf, ReplaceRuleBody, StrictCallTransformer

from pegen.grammar import StringLeaf

class WhenTransformer(Transform):
    
    def __init__(self):
        self.iftowhen = RenameLeaf(StringLeaf, "'if'", "'when'")
        self.eliftoelwhen = RenameLeaf(StringLeaf, "'elif'", "'elwhen'")
        
    def apply_grammar(self, grammar):
        self.iftowhen.apply(grammar)
        self.eliftoelwhen.apply(grammar)
        
class SemiColonTransformer(Transform):
    
    def __init__(self):
        self.replace = ReplaceRuleBody("simple_stmts", """simple_stmts[list]:
    | a=simple_stmt ';' NEWLINE { [a] } # Not needed, there for speedup
    | a=';'.simple_stmt+ ';' NEWLINE { a }""")
        
    def apply_grammar(self, grammar):
        self.replace.apply(grammar)
        
class PrintScreenTransformer(Transform):
    
    def __init__(self):
        self.name_t = StrictCallTransformer("print_screen", "print")
        
    def apply_ast(self, root):
        self.name_t.visit(root)