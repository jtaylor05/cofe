from typing import Any

import argparse
from pathlib import Path
import subprocess
import sys

type PathLike = str | Path

def get_cli():
    parser = argparse.ArgumentParser(prog="cofe-exec", description="Module to execute python files in the current cofe environment.")
    parser.add_argument("file", type=Path, help="File to execute.")
    return parser

def exec_python(file_path: PathLike, *args) -> Any:
    subprocess.call([
        sys.executable, 
        "-c", 
        "from cofe.preprocess.loader import execute_file; execute_file()",
        str(Path(file_path).resolve()),
        *args
    ])
    
def main(args):
    parser = get_cli()
    parsed, remaining = parser.parse_known_args(args)
    
    exec_python(parsed.file, *remaining)