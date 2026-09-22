import sys

import random

import argparse as ap

from typing import Literal
from pathlib import Path

from . import PythonLauncher, PackageConfigParser, install_import_hook, TEST_MODE
from .utils import get_transformers, gather_transformers

type PathsOrNames = Path | str
type ConfigState = Literal['active', 'available']

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
        for cls, fp in [(cls, fp) for target in targets for cls, fp in get_transformers(target)]:
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
            
def find_transformers(state: ConfigState, roots: list[Path], parser: PackageConfigParser = None):
    config = PackageConfigParser() if parser is None else parser
    
    targets = [(cls, fp) for root in roots for cls, fp in gather_transformers(root)]
    if state == 'available':
        for cls, fp in targets:
            config.add_transformer(cls.__name__, fp)
    else:
        for name in _get_transformer_names(targets):
            config.add_active(name)
            
def list_transformers(state: ConfigState, parser: PackageConfigParser = None):
    config = PackageConfigParser() if parser is None else parser
    
    if state == 'available':
        print("Available Transformers:")
        for name, file in config.get_available().items():
            print(f"{name:>30.30} : {file:.100}")
    else:
        print("Active Transformers:")
        for name, file in config.get_active().items():
            print(f"{name:>30.30} : {file:.100}")

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

def exec_command(file_path: str, remainder: list[str], debug=False, config_file=None):
    sys.argv = [file_path] + remainder
    print(sys.argv)
    
    install_import_hook()
    
    launcher = PythonLauncher(file_path, config_file) if config_file else PythonLauncher(file_path)
    launcher.launch(debug) 

def normal_mode():
    parser = ap.ArgumentParser(
        prog="cofe",
        description="A COunterFactual Environment python interpreter; completely compatible with standard python.",
        epilog="This project is under development. There may still be bugs."
    )
    subparsers = parser.add_subparsers(dest="command", required=True, help="Which submodule to use.")
    
    config_parser = subparsers.add_parser("config", help="configure interpreter settings and modules.")
    
    main_grp = config_parser.add_argument_group("Main Operations")
    main_grp.add_argument("-v", "--active", action='store_true', help="Performs all main operations on the active list, rather than the available.")
    main_grp.add_argument("-a", "--add", dest="targets", nargs='*', type=str, help="Add all valid transformers in a file.")
    main_grp.add_argument("-r", "--remove", dest="remove_targets", nargs='*', type=str, help="Attempts to remove either transformer with same class name as input, or all transformers from input file.")
    main_grp.add_argument("-f", "--find", dest="roots", nargs='*', type=Path, help="Recursively find all transformers starting from directory root and add them.")
    main_grp.add_argument("-l", "--list", action='store_true', help="Lists out transformers.")
    
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
    
    # freeze_parser = subparsers.add_parser("freeze", help="Freezes current state into an executable. Executable can only execute code.")
    # freeze_parser.add_argument("-o", "--output", type=str, default="cofe", help="File name of saved executable.")
    
    args, remainder = parser.parse_known_args()
    
    match args.command:
        case "config":
            state = 'active' if args.active else 'available'
            config = PackageConfigParser()
            
            # Restore to defaults first if desired.
            if args.restore:
                config.restore()
            
            # Main Operations
            ## add op
            if args.targets:
                add_transformers(state, args.targets, config)
            ## remove op
            if args.remove_targets:
                remove_transformers(state, args.remove_targets, config)
            ## find op
            if args.roots:
                find_transformers(state, args.roots, config)
            ## list op
            if args.list:
                list_transformers(state, config)
            
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
            exec_command(args.file_path, remainder, args.cofe_debug, args.cofe_tag)

def test_mode():
    parser = ap.ArgumentParser(
        prog="cofe",
        description="A COunterFactual Environment python interpreter; completely compatible with standard python.",
        epilog="This project is under development. There may still be bugs."
    )
    parser.add_argument("file_path", type=str)

    parser.add_argument("--end-test", action="store_true", help=ap.SUPPRESS)

    args, remainder = parser.parse_known_args()
    
    exec_command(args.file_path, remainder, False)
    
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
            
            