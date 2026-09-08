import sys

import random

import argparse as ap

from . import PythonLauncher, PackageConfigParser, install_import_hook

def add_changes(raw_changes: list[str]):
    print("changes:", raw_changes)
    changes = {d[0]:d[1] for d in [c.split('=') for c in raw_changes]}
    
    config = PackageConfigParser()
    for k,v in changes.items():
        config.set_default(k, v)
    
    config.write()
    
def add_transformers(raw_transformers: list[str]):
    print("transformers: ", raw_transformers)
    transformers = {d[0]:d[1] for d in [t.split('=') for t in raw_transformers]}
    
    config = PackageConfigParser()
    for k, v in transformers.items():
        config.add_transformer(k, v)
        
    config.write()
    
def add_active(new_active: list[str]):
    print("New active: ", new_active)
    
    config = PackageConfigParser()
    for a in new_active:
        config.add_active(a)
    
    config.write()
    
def remove_transformers(old_transformers: list[str]):
    config = PackageConfigParser()
    for t in old_transformers:
        config.remove_transformer(t)
    config.write()
    
def remove_active(old_active: list[str]):
    config = PackageConfigParser()
    for a in old_active:
        config.remove_active(a)
    config.write()

def randomize_active(n: int):
    config = PackageConfigParser()
    
    config.clear_active()
    
    classes = [k for k,_ in config.get_available().items()]
    
    selection = random.sample(classes, n)
    
    for s in selection:
        config.add_active(s)
        
    config.write()
    

def exec_command(file_path: str, remainder: list[str], debug=False):
    sys.argv = [file_path] + remainder
    print(sys.argv)
    
    install_import_hook()
    
    launcher = PythonLauncher(file_path)
    launcher.launch(debug) 

if __name__ == "__main__":
    parser = ap.ArgumentParser(
        prog="ython",
        description="A counterfactual python interpreter; completely compatible with standard python.",
        epilog="This project is under development. There may still be bugs."
    )
    subparsers = parser.add_subparsers(dest="command", required=True, help="Which submodule to use.")
    
    config_parser = subparsers.add_parser("config", help="configure interpreter settings and modules.")
    config_parser.add_argument("-c", "--change", nargs='*', type=str, help="Changes made to current configuration (key=value).")
    config_parser.add_argument("-r", "--restore", action='store_true', help="Restores defaults on the current configuration.")
    config_parser.add_argument("-t", "--transformer", nargs='*', type=str, help="Add new transformer class, as well as file (cls=file).")
    config_parser.add_argument("-a", "--active", nargs='*', type=str, help="Add new active transformer class.")
    config_parser.add_argument("-v", "--remove-available", nargs='*', type=str, help="Remove transformer class from available.")
    config_parser.add_argument("-l", "--remove-active", nargs='*', type=str, help="Remove transformer class from active.")
    config_parser.add_argument("-R", "--random", type=int, default=-1, help="Randomize active transformers.")
    
    exec_parser = subparsers.add_parser("exec", help="acts as an entry point into module code.")
    exec_parser.add_argument("file_path", type=str)
    exec_parser.add_argument("--debug-cofe", action="store_true", help="A hook to include all of the stack in the traceback.")
    
    # freeze_parser = subparsers.add_parser("freeze", help="Freezes current state into an executable. Executable can only execute code.")
    # freeze_parser.add_argument("-o", "--output", type=str, default="cofe", help="File name of saved executable.")
    
    args, remainder = parser.parse_known_args()
    
    match args.command:
        case "config":
            if args.restore:
                PackageConfigParser().restore()
            if args.change:
                add_changes(args.change)
            if args.transformer:
                add_transformers(args.transformer)
            if args.active:
                add_active(args.active)
            if args.remove_available:
                remove_transformers(args.remove_available)
            if args.remove_active:
                remove_active(args.remove_active)
            if args.random >= 0:
                randomize_active(args.random)
            
        case "exec":
            exec_command(args.file_path, remainder, args.debug_cofe)
            
            