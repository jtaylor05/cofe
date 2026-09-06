import sys, ast
from typing import Any, Type

from importlib import util

from pathlib import Path

from .configure import PackageConfigParser, Transform
from .grammar_transform import GrammarWrapper
from .utils import get_python_grammar, parse_from_grammar

type PathLike = str | Path  
type Module = Any
type SysArgs = list[str]

class InvalidExtensionError(Exception):
    """Raise error when the extension to a file is invalid."""
    pass

class PythonLauncher:
    def __init__(self, file: PathLike, custom_config: PackageConfigParser = None):
        self.config = custom_config if custom_config != None else PackageConfigParser()
        
        _modules = {}
        
        self.transformers: list[Transform] = []
        
        for cls, f in self.config.get_active().items():
            p = Path(f)
            module_name = p.name
            
            if module_name in _modules:
                class_var = getattr(_modules[module_name], cls)
                if issubclass(class_var, Transform):
                    self.transformers.append(class_var())
                continue
            
            module = import_module_from_file(module_name, p)
            
            _modules[module_name] = module
            class_var = getattr(module, cls)
            if issubclass(class_var, Transform):
                self.transformers.append(class_var())
        
        self.transformers.sort(key=lambda t: t.get_sort())
        
        if not Path(file).exists():
            raise FileExistsError(f"File {file} given to PythonLauncher does not exist.")
        if not self._file_has_valid_extension(file):
            raise InvalidExtensionError(f"{file} has extension {Path(file).suffix}. Extension {self.config.extension} expected.")
        
        self.file = file
        
    def launch(self):
        with open(self.file, 'r') as f:
            src = f.read()
        
        grammar = GrammarWrapper(get_python_grammar())
        
        for t in self.transformers:
            t.apply_grammar(grammar)
            
        root = parse_from_grammar(src, grammar)
        
        for t in self.transformers:
            t.apply_ast(root)
            
        transformed = ast.unparse(root)
        
        code = compile(transformed, self.file, 'exec')
        
        global_scope = {'__name__': '__main__', '__file__': self.file}
        local_scope = {}
        
        print("=================EXECUTION BEGINS=================")
        
        exec(code, globals=global_scope, locals=local_scope)
        
    def _file_has_valid_extension(self, file: PathLike):
        return Path(file).suffix == self.config.extension

def import_module_from_file(module_name: str, file_path: PathLike):
    spec = util.spec_from_file_location(module_name, file_path)
    
    module = util.module_from_spec(spec)
    
    sys.modules[module_name] = module
    
    spec.loader.exec_module(module)
    
    return module