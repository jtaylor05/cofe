import sys

from pathlib import Path

from .configure import YthonConfigParser

type PathLike = str | Path  
type SysArgs = list[str]

class InvalidExtensionError(Exception):
    """Raise error when the extension to a file is invalid."""
    pass

class PythonLauncher:
    def __init__(self, file: PathLike, custom_config: YthonConfigParser = None):
        self.config = custom_config if custom_config != None else YthonConfigParser()
        
        if not Path(file).exists():
            raise FileExistsError(f"File {file} given to PythonLauncher does not exist.")
        if not self._file_has_valid_extension(file):
            raise InvalidExtensionError(f"{file} has extension {Path(file).suffix}. Extension {self.config.extension} expected.")
        
        self.file = file
        
    def launch(self):
        with open(self.file, 'r') as f:
            src = f.read()
        
        #TODO: implement hook for transforming code
        transformed = src
        
        code = compile(transformed, self.file, 'exec')
        
        global_scope = {'__name__': '__main__', '__file__': self.file}
        local_scope = {}
        
        print("=================EXECUTION BEGINS=================")
        
        exec(code, globals=global_scope, locals=local_scope)
        
    def _file_has_valid_extension(self, file: PathLike):
        return Path(file).suffix == self.config.extension
