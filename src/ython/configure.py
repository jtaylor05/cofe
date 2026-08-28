from configparser import ConfigParser
from pathlib import Path

MODULE_DIR = ".cenv"

CONFIG_FILENAME = "config.ini"

EXTENSION = "extension_name"

class InvalidConfigError(Exception):
    """Raised when a config value does not exist in the configuration."""
    pass

class YthonConfigParser(ConfigParser):
    def __init__(self, directory: str = MODULE_DIR, config_file: str = CONFIG_FILENAME):
        super().__init__()
        self.config_file = Path(directory, config_file).resolve()
        if not self.config_file.exists():
            init_config_settings(self.config_file)
        
        self.read(self.config_file)
    
    @property
    def extension(self):
        if EXTENSION not in self['DEFAULT']:
            raise InvalidConfigError(f"No value 'extension' can be found in {CONFIG_FILENAME}.")
        return self['DEFAULT'][EXTENSION]
    
    def set(self, key: str, val):
        self['DEFAULT'][key][val]
    
    def write(self):
        with open(self.config_file, 'r') as cf:
            super().write(cf)
    
def init_config_settings(file: Path):
    file.parent.mkdir(parents=True, exist_ok=True)
    
    parser = ConfigParser()
    parser['DEFAULT'] = { EXTENSION : '.y' }
    with open(file, 'w') as cf:
        parser.write(cf)