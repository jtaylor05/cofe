import argparse
from pathlib import Path
import sys

from cofe.config.configure import PackageConfigParser
from cofe.utils import gather_transformers, get_transformers

type PathsOrNames = Path | str

def get_cli():
    parser = argparse.ArgumentParser(prog="cofe-config", description="Module to configure current cofe environment.")
    
    tag_grp = parser.add_argument_group("Tag Operations")
    tag_grp.add_argument("-t", "--tag", type=str, help="Saves a copy of the current configuration to a new file at this location.")
    tag_grp.add_argument("-s", "--set", type=Path, help="Replaces current config with the given config. Does not save the old one.")
    
    cmd_subparsers = parser.add_subparsers(title="op", dest="cmd")
    
    add = cmd_subparsers.add_parser("add", help="Add transformers to the current environment.")
    add.add_argument("transformers", nargs='+', help="Files and class names to be added.")
    
    rem = cmd_subparsers.add_parser("remove", help="Remove transformers from the current environment.")
    rem.add_argument("transformers", nargs='+', help="Files and class names to be removed.")
    
    find = cmd_subparsers.add_parser("find", help="Find transformers in the current environment.")
    find.add_argument("paths", nargs='+', help="Files and class names to be removed.")
    find.add_argument("-d", "--depth", type=int, default=5, help="Recursive depth of search.")
    
    list = cmd_subparsers.add_parser("list", help="Displays the config file.")
    
    return parser
    
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


def add_transformers(targets: list[PathsOrNames], parser: PackageConfigParser = None):
    config = PackageConfigParser() if parser is None else parser
    for name in _get_transformer_names(targets):
        config.add_active(name)
    
def remove_transformers(targets: list[PathsOrNames], parser: PackageConfigParser = None):
    config = PackageConfigParser() if parser is None else parser
       
    for name in _get_transformer_names(targets):
        config.remove_active(name)

def find_transformers(roots: list[Path], parser: PackageConfigParser = None, depth=5):
    config = PackageConfigParser() if parser is None else parser
    
    targets = [(cls, fp) for root in roots for cls, fp in gather_transformers(root, depth=depth)]
    try:
        for cls, fp in targets:
            config.add_transformer(cls.__name__, fp)
    except Exception as e:
        raise ValueError(f"Input file is incorrect. {e}")
    
def display_config(parser: PackageConfigParser = None):
    config = PackageConfigParser() if parser is None else parser
    config.write(sys.stdout)
    
def main(args):
    parser = get_cli()
    args = parser.parse_args(args)
    
    if args.set:
        config = PackageConfigParser(args.set)
        config.write()
        sys.exit(0)
    
    if args.cmd:
        match args.cmd:
            case "add":
                add_transformers(args.transformers)
            case "remove":
                remove_transformers(args.transformers)
            case "find":
                find_transformers([Path(p) for p in args.paths], depth=args.depth)
            case "list":
                display_config()
                
    if args.tag:
        config = PackageConfigParser()
        config.save(args.tag)