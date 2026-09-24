from configparser import ConfigParser
from pathlib import Path

import warnings, os

MODULE_DIR = os.environ.get("COFE_DATA_DIR", ".cenv")

CONFIG_FILENAME = "config.ini"

EXTENSION = "extension"
TEST_MODE = "test"

type Pathlike = str | Path

def init_config_settings(parser: ConfigParser):
    parser.optionxform = str
    parser['env'] = { EXTENSION : '.y', 
                          TEST_MODE : "False"}
        
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
            if not self.has_option("env", EXTENSION):
                self.set("env", EXTENSION, '.y')
            if not self.has_option("env", TEST_MODE):
                self.set("env", TEST_MODE, "False")
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
            warnings.warn(f"No value {TEST_MODE} can be found in {self.config_file}.")
            return False
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
            print(f"WARNING: {cls_name} not one of the available transformers. Skipping.")
            return
        self.set('active', cls_name, self['available'][cls_name])
        
    def remove_active(self, cls_name: str):
        self.remove_option('active', cls_name)
        
    def clear_active(self):
        for cls_name in self['active']:
            self.remove_active(cls_name)

    def get_active(self) -> dict[str, str]:
        return dict(self['active'])
    
    def load(self, file=None):
        fp = self.config_file if file is None else file
        self.clear()
        self.read(fp)
    
    def write(self, dest=None):
        fp = self.config_file if dest is None else dest
        try:
            Path(fp).parent.mkdir(parents=True, exist_ok=True)
            with open(fp, 'w') as cf:
                super().write(cf)
        except:
            super().write(dest)
    
    def restore(self):
        init_config_settings(self)