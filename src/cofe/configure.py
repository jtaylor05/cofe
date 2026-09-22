from configparser import ConfigParser
from pathlib import Path

import ast

from .grammar_transform import GrammarWrapper, RenameStringLeaf, ReplaceRuleBody
from .ast_transform import (
    StrictCallTransformer,
    AggregateImportTransformer
)

MODULE_DIR = ".cenv"

CONFIG_FILENAME = "config.ini"

EXTENSION = "extension"
TEST_MODE = "test"

type Pathlike = str | Path

def init_config_settings(parser: ConfigParser):
    parser.optionxform = str
    parser['env'] = { EXTENSION : '.y', 
                          TEST_MODE : False}
        
    parser['available'] = {}
    
    parser['active'] = {}


class InvalidConfigError(Exception):
    """Raised when a config value does not exist in the configuration."""
    pass

class PackageConfigParser(ConfigParser):
    def __init__(self, config_file: str = Path(MODULE_DIR, CONFIG_FILENAME)):
        super().__init__()
        self.optionxform = str
        
        self.config_file = Path(config_file).resolve()
        if not self.config_file.exists():
            init_config_settings(self)
            self.write()
        
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
            raise InvalidConfigError(f"No value '{EXTENSION}' can be found in {CONFIG_FILENAME}.")
        return self['env'][EXTENSION]
    
    @property
    def test_mode(self):
        if TEST_MODE not in self['env']:
            raise InvalidConfigError(f"No value '{TEST_MODE}' can be found in {CONFIG_FILENAME}.")
        return self['env'].getboolean(TEST_MODE)
    
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
    
    def write(self, dest=None):
        fp = self.config_file if dest is None else dest
        with open(fp, 'w') as cf:
            super().write(cf)
    
    def restore(self):
        init_config_settings(self)
        
        
def matches_transform(cls: type):
    properties_transform = { attr for attr in dir(Transform) }
    properties_cls = { attr for attr in dir(cls) }
    
    return properties_transform.issubset(properties_cls)

class Transform:
        
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
   