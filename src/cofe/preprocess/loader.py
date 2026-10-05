import sys

import importlib.machinery
from pathlib import Path

from cofe.config.configure import PackageConfigParser
from cofe.transform.transform import transform_code

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