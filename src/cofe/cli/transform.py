from __future__ import annotations

import argparse
from pathlib import Path
from typing import Union

from cofe.transform.transform import transform_code

PathLike = Union[str, Path]

def get_cli():
    parser = argparse.ArgumentParser(prog="cofe-transform", description="Module to transform python files in the current cofe environment.")
    
    cmd_subparsers = parser.add_subparsers(title="op", dest="cmd")
    
    from_parser = cmd_subparsers.add_parser("from", help="Transform a file to another file.")
    from_parser.add_argument("source", type=str, help="Python or cofe environment file.")
    from_parser.add_argument("--to", type=str, required=True, help="Output file path. If not provided, will print to stdout.")
    from_parser.add_argument("-c", "--config", type=str, help="Path to a config file to use for the transformation. If not provided, will use the current environment config.")
    
    return parser

def transform_file(source: PathLike, output: PathLike = None, config: PathLike = None):
    source_path = Path(source)
    output_path = Path(output) if output else None
    config_path = Path(config) if config else None

    with open(source_path, "r") as f:
        source_code = f.read()

    transformed_code = transform_code(source_code, config_file=config_path)

    if output_path:
        with open(output_path, "w") as f:
            f.write(transformed_code)
    else:
        print(transformed_code)

def main(args):
    parser = get_cli()
    parsed = parser.parse_args(args)
    
    if parsed.cmd:
        if parsed.cmd == "from":
            pass
    
    