import sys

import importlib.machinery
from pathlib import Path

from .configure import YthonConfigParser

class PreProcessExtensionLoader(importlib.machinery.SourceFileLoader):
    def get_data(self, path):
        # Gets file's bytes at path.
        
        config = YthonConfigParser()
        
        raw = super().get_data(path)
        
        if Path(path).suffix == config.extension:
            source_text = raw.decode('utf-8')
            transformed = transform_code(source_text)
            return transformed.encode('utf-8')
        
        return raw

    def source_to_code(self, data, path, *, _optimize=-1):
        return super().source_to_code(data, path, _optimize=_optimize)

def install_import_hook():
    config = YthonConfigParser()
    
    loader_details = (PreProcessExtensionLoader, [config.extension])
    path_hook = importlib.machinery.FileFinder.path_hook(loader_details)

    # Insert before the default hooks so it takes priority
    sys.path_hooks.insert(0, path_hook)

    # Clear the finder cache so existing sys.path entries pick up the new hook
    sys.path_importer_cache.clear()
    
def transform_code(source: str) -> str:
    return source