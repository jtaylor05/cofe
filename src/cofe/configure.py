from configparser import ConfigParser
from pathlib import Path

import ast

from .grammar_transform import GrammarWrapper, RenameLeaf, ReplaceRuleBody
from .ast_transform import StrictCallTransformer
from pegen.grammar import StringLeaf

MODULE_DIR = ".cenv"

CONFIG_FILENAME = "config.ini"

EXTENSION = "extension"

type Pathlike = str | Path

class InvalidConfigError(Exception):
    """Raised when a config value does not exist in the configuration."""
    pass

class PackageConfigParser(ConfigParser):
    def __init__(self, directory: str = MODULE_DIR, config_file: str = CONFIG_FILENAME):
        super().__init__()
        self.optionxform = str
        
        self.config_file = Path(directory, config_file).resolve()
        if not self.config_file.exists():
            init_config_settings(self.config_file)
        
        self.read(self.config_file)
        
        if not self.has_section("env"):
            self.add_section("env")
        if not self.has_section("available"):
            self.add_section("available")
        if not self.has_section("active"):
            self.add_section("active")
    
    @property
    def extension(self):
        if EXTENSION not in self['env']:
            raise InvalidConfigError(f"No value 'extension' can be found in {CONFIG_FILENAME}.")
        return self['env'][EXTENSION]
    
    def set_default(self, key: str, val: str):
        if key in self['env']:
            self['env'][key] = val
        else:
            raise ValueError(f"Key {key} is not contained in 'env'.")
        
    def add_transformer(self, cls_name: str, cls_file: Pathlike):
        self.set('available', cls_name, str(Path(cls_file)))
        
    def remove_transformer(self, cls_name: str):
        self.remove_option('available', cls_name)
        
    def get_available(self) -> dict[str, str]:
        return dict(self['available'])
        
    def add_active(self, cls_name: str):
        if cls_name not in self['available']:
            raise InvalidConfigError(f"{cls_name} not one of the available transformers.")
        self.set('active', cls_name, self['available'][cls_name])
        
    def remove_active(self, cls_name: str):
        self.remove_option('active', cls_name)
        
    def clear_active(self):
        for cls_name in self['active']:
            self.remove_active(cls_name)

    def get_active(self) -> dict[str, str]:
        return dict(self['active'])
    
    def write(self):
        with open(self.config_file, 'w') as cf:
            super().write(cf)
    
    def restore(self):
        self.config_file.unlink(True)
        init_config_settings(self.config_file)
    
def init_config_settings(file: Path):
    file.parent.mkdir(parents=True, exist_ok=True)
    
    parser = ConfigParser()
    parser.optionxform = str
    parser['env'] = { EXTENSION : '.y' }
    
    fp = Path(__file__).resolve()
    parser['available'] = {
        WhenTransformer.__name__:fp,
        PrintScreenTransformer.__name__:fp,
        SemiColonTransformer.__name__:fp
    }
    
    parser['active'] = {}
    with open(file, 'w') as cf:
        parser.write(cf)
        
class Transform:
    
    TRANSFORM_REGISTRY = {}
    
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.TRANSFORM_REGISTRY[cls.__name__] = cls
        
    def apply_grammar(self, grammar : GrammarWrapper):
        pass
    
    def apply_ast(self, root : ast.AST):
        pass
    
    
    def get_sort(self):
        return 0
        
    def __lt__(self, other):
        if not isinstance(other, Transform):
            raise NotImplementedError("Can only compare with other Transform subclasses.")
        return self.get_sort() < other.get_sort()
    
    def __le__(self, other):
        if not isinstance(other, Transform):
            raise NotImplementedError("Can only compare with other Transform subclasses.")
        return self.get_sort() <= other.get_sort()
    
    def __eq__(self, other):
        if not isinstance(other, Transform):
            raise NotImplementedError("Can only compare with other Transform subclasses.")
        return self.get_sort() == other.get_sort()
    
    def __ne__(self, other):
        if not isinstance(other, Transform):
            raise NotImplementedError("Can only compare with other Transform subclasses.")
        return self.get_sort() != other.get_sort()
    
    def __ge__(self, other):
        if not isinstance(other, Transform):
            raise NotImplementedError("Can only compare with other Transform subclasses.")
        return self.get_sort() >= other.get_sort()
    
    def __gt__(self, other):
        if not isinstance(other, Transform):
            raise NotImplementedError("Can only compare with other Transform subclasses.")
        return self.get_sort() > other.get_sort()
    
    def __hash__(self):
        return object.__hash__(self)
    
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