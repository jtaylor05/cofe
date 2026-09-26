import ast
import sys
import functools

import importlib.machinery
from pathlib import Path

from .configure import PackageConfigParser
from .grammar_transform import GrammarWrapper
from .transform import Transform, matches_transform
from .utils import get_python_grammar, import_module_from_file, parse_from_grammar

@functools.cache
def get_transformer_src():
    config = PackageConfigParser()
    
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

def transform_code(source: str) -> str:
    grammar = GrammarWrapper(get_python_grammar())
    
    transformers = get_transformer_src()
            
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

    return transformed

def execute_file():
    """Execute the target file after installing the import hook."""
    install_import_hook()

    file_path = str(Path(sys.argv[1]).resolve())
    sys.argv[:] = [file_path, *sys.argv[2:]]
    sys.path[0] = str(Path(file_path).parent)
    loader = PreProcessExtensionLoader("__main__", file_path)
    source = loader.get_data(file_path)
    code = loader.source_to_code(source, file_path)

    main_globals = {
        "__name__": "__main__",
        "__file__": file_path,
        "__package__": None,
        "__cached__": None,
        "__builtins__": __builtins__,
    }
    exec(code, main_globals, main_globals)

def install_import_hook():
    config = PackageConfigParser()
    
    loader_details = [
        (PreProcessExtensionLoader, [config.extension]),
        (importlib.machinery.SourceFileLoader, importlib.machinery.SOURCE_SUFFIXES)
    ]
    path_hook = importlib.machinery.FileFinder.path_hook(*loader_details)

    # Insert before the default hooks so it takes priority
    sys.path_hooks.insert(0, path_hook)

    # Clear the finder cache so existing sys.path entries pick up the new hook
    sys.path_importer_cache.clear()

class PreProcessExtensionLoader(importlib.machinery.SourceFileLoader):
    def get_data(self, path):
        # Gets file's bytes at path.
        
        config = PackageConfigParser()
        
        raw = super().get_data(path)
        
        if Path(path).suffix == config.extension:
            source_text = raw.decode('utf-8')
            transformed = transform_code(source_text)
            return transformed.encode('utf-8')
        
        return raw

    def source_to_code(self, data, path, *, _optimize=-1):
        return super().source_to_code(data, path, _optimize=_optimize)