import argparse as ap
import sys
import subprocess
import random
from typing import Literal
from pathlib import Path

from .configure import PackageConfigParser, TEST_MODE
from .utils import get_transformers, gather_transformers

type PathsOrNames = Path | str
type ConfigState = Literal['active', 'available']

def _verify_filenames(targets: list[PathsOrNames]) -> list[Path]:
    return [Path(t) for t in targets if Path(t).exists()]

def _get_transformer_names(targets: list[PathsOrNames]) -> list[str]:
    paths = []
    cls_names = []
    for t in targets: 
        path = Path(t)
        if path.exists():
            paths.append(path)
        else:
            cls_names.append(t)
    
    return cls_names + [cls.__name__ for p in paths for cls, _ in get_transformers(p)]

#=========================================== MAIN OPERATIONS =================================================#

def add_transformers(state: ConfigState, targets: list[PathsOrNames], parser: PackageConfigParser = None):
    config = PackageConfigParser() if parser is None else parser
    
    if state == 'available':
        for cls, fp in [(cls, fp) for target in _verify_filenames(targets) for cls, fp in get_transformers(target)]:
            config.add_transformer(cls.__name__, fp)
    else:
        for name in _get_transformer_names(targets):
            config.add_active(name)
    
def remove_transformers(state: ConfigState, targets: list[PathsOrNames], parser: PackageConfigParser = None):
    config = PackageConfigParser() if parser is None else parser
        
    if state == 'available':
        for name in _get_transformer_names(targets):
            config.remove_transformer(name)
    else:
        for name in _get_transformer_names(targets):
            config.remove_active(name)
            
def find_transformers(state: ConfigState, roots: list[Path], parser: PackageConfigParser = None, depth=5):
    config = PackageConfigParser() if parser is None else parser
    
    targets = [(cls, fp) for root in roots for cls, fp in gather_transformers(root, depth=depth)]
    if state == 'available':
        try:
            for cls, fp in targets:
                config.add_transformer(cls.__name__, fp)
        except Exception as e:
            raise ValueError(f"Input file is incorrect. {e}")
    else:
        for name in [c.__name__ for c, _ in targets]:
            config.add_active(name)
   
def display_config(parser: PackageConfigParser = None):
    config = PackageConfigParser() if parser is None else parser
    
    config.write(sys.stdout)

#=============================================================================================================#

def add_changes(raw_changes: list[str]):
    print("changes:", raw_changes)
    changes = {d[0]:d[1] for d in [c.split('=') for c in raw_changes]}
    
    config = PackageConfigParser()
    for k,v in changes.items():
        config.set_default(k, v)
    
    config.write()
    
def deactivate(parser: PackageConfigParser=None):
    config = PackageConfigParser() if parser is None else parser
    config.clear_active()

def randomize_active(n: int, parser: PackageConfigParser=None):
    config = PackageConfigParser() if parser is None else parser
    
    config.clear_active()
    
    classes = [k for k,_ in config.get_available().items()]
    
    selection = random.sample(classes, n)
    
    for s in selection:
        config.add_active(s)

def tag_config(file_path: str, parser: PackageConfigParser=None):
    config = PackageConfigParser() if parser is None else parser
    
    config.write(file_path)
    
def set_tag(file_path: str, parser: PackageConfigParser):
    parser.load(file_path)

def exec_command(file_path: str, remainder: list[str]):
    child_bootstrap = "from cofe.preprocess import execute_file; execute_file()"
    subprocess.call([
        sys.executable,
        "-c",
        child_bootstrap,
        str(Path(file_path).resolve()),
        *remainder,
    ])

def normal_mode():
    parser = ap.ArgumentParser(
        prog="cofe",
        description="A COunterFactual Environment python interpreter; completely compatible with standard python.",
        epilog="This project is under development. There may still be bugs."
    )
    subparsers = parser.add_subparsers(dest="command", required=True, help="Which submodule to use.")
    
    config_parser = subparsers.add_parser("config", help="configure interpreter settings and modules.")
    
    # Main actions
    main_grp = config_parser.add_argument_group("Main Operations")
    main_subparser = config_parser.add_subparsers(dest="op", help="Operation to perform on active or available list.")
    
    # Add action
    add_parser = main_subparser.add_parser("add", help="Add transformers and file paths to the available list on your configuration.")
    add_parser.add_argument("transformers", nargs='+', help="Files and class names to be added.")
    add_parser.add_argument("-v", "--active", action='store_true', help="Adds files/classes to the active list, rather than the available.")
    
    # Remove action
    rem_parser = main_subparser.add_parser("remove", help="Remove transformers and file paths from the available list of your configuration")
    rem_parser.add_argument("transformers", nargs='+', help="Files and class names to be removed.")
    rem_parser.add_argument("-v", "--active", action='store_true', help="Removes files/classes from the active list, rather than the available.")
    
    # Find action
    find_parser = main_subparser.add_parser("find", help="Find transformers and file paths recursively from root folders.")
    find_parser.add_argument("paths", nargs='+', help="Files and class names to be removed.")
    find_parser.add_argument("-v", "--active", action='store_true', help="Adds files/classes to the active list, rather than the available.")
    find_parser.add_argument("-D", "--depth", type=int, default=5, help="Recursive depth of search.")
    
    # List action
    list_parser = main_subparser.add_parser("list", help="Displays the config file.")
    
    config_parser.add_argument("-c", "--change", nargs='*', type=str, help="Changes made to current configuration (key=value).")
    config_parser.add_argument("-R", "--restore", action='store_true', help="Restores defaults on the current configuration.")
    config_parser.add_argument("-d", "--deactivate", action='store_true', help="Removes all active transformers.")
    config_parser.add_argument("--random", type=int, default=-1, help="Randomize n active transformers.")
    
    tag_grp = config_parser.add_argument_group("Tag Operations")
    tag_grp.add_argument("-t", "--tag", type=str, help="Saves a copy of the current configuration to a new file at this location.")
    tag_grp.add_argument("-s", "--set", type=Path, help="Replaces current config with the given config. Does not save the old one.")
    
    
    exec_parser = subparsers.add_parser("exec", help="acts as an entry point into module code.")
    exec_parser.add_argument("file_path", type=str)
    exec_parser.add_argument("--cofe-debug", action="store_true", help="A hook to include all of the stack in the traceback.")
    #If given, uses this file as config instead of standard.
    exec_parser.add_argument("--cofe-tag", type=str, help="If given, uses this file as config instead of standard.")
    
    args, remainder = parser.parse_known_args()
    
    match args.command:
        case "config":
            config = PackageConfigParser()
            
            if args.op in ("add", "remove", "find"):
                state = 'active' if args.active else 'available'
                match args.op:
                    case "add":
                        add_transformers(state, args.transformers, config)
                    case "remove":
                        remove_transformers(state, args.transformers, config)
                    case "find":
                        find_transformers(state, args.paths, config, depth=args.depth)
            elif args.op == "list":
                display_config(config)   
            else:
                # Restore to defaults first if desired.
                if args.restore:
                    config.restore()
            
                # Other Operations
                ## config mod op
                if args.change:
                    add_changes(args.change)
                ## deactivate op
                if args.deactivate:
                    deactivate(config)
                ## randomize op
                if args.random >= 0:
                    randomize_active(args.random, config)
                    
                # Tag Operations
                if args.tag:
                    tag_config(args.tag, config)
                if args.set:
                    set_tag(args.set, config)
            config.write()
            
        case "exec":
            exec_command(args.file_path, remainder)

def test_mode():
    parser = ap.ArgumentParser(
        prog="cofe",
        description="A COunterFactual Environment python interpreter; completely compatible with standard python.",
        epilog="This project is under development. There may still be bugs."
    )
    parser.add_argument("file_path", type=str)

    parser.add_argument("--end-test", action="store_true", help=ap.SUPPRESS)

    args, remainder = parser.parse_known_args()
    
    exec_command(args.file_path, remainder)
    
    if args.end_test:
        conf = PackageConfigParser()
        conf.set_default(TEST_MODE, False)
        conf.write()
    

def main():
    conf = PackageConfigParser()
    if conf.test_mode:
        test_mode()
    else:
        normal_mode()
        

if __name__ == "__main__":
    main()
            
            