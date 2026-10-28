import libcst as cst

Module = cst.Module

def get_cst(file_path: str) -> Module:
    with open(file_path, 'r') as f:
        source = f.read().encode(encoding="utf-8")
        
    return cst.parse_module(source)

class CofeUnparser(cst.CSTVisitor):
    def __init__(self):
        self.unparsed = ""
        
    def unparse(self, node: cst.CSTNode) -> str:
        node.visit(self)
        return self.unparsed

