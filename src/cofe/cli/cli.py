import argparse
import subprocess
import sys

from importlib.metadata import version

from cofe.cli.config import main as config_main
from cofe.cli.exec import main as exec_main
from cofe.cli.transform import main as transform_main

_AVAILABLE_MODULES = {
    "config",
    "transform",
    "exec"
}

def get_cli():
    parser = argparse.ArgumentParser(
        prog="cofe", 
        description="A CounterFactual Environment python interpreter; completely compatible with standard python.",
        add_help=False)
    parser.add_argument("-v", "--version", action="version", version=f"cofe {version('cofe')}")
    parser.add_argument("-h", "--help", action="store_true")
    parser.add_argument("-m", nargs=argparse.REMAINDER, dest="mod", type=str)
    return parser

def run_help(executable: str, new_name: str = "cofe") -> None:
    out = subprocess.run([executable, "-h"], capture_output=True, text=True).stdout
    out = out.replace(f'usage: {executable}', f'usage: {new_name}')
    print(out)
    
def run_cmd(executable: str, *args) -> None:
    subprocess.run([executable, *args], check=True)

def handle_custom_module(module: str, args=None):
    args = [] if args is None else args
    
    match module:
        case "config":
            config_main(args)
        
        case "exec":
            exec_main(args)
        
        case "transform":
            transform_main(args)

def main():
    args = sys.argv[1:]
    cli = get_cli()
    parsed, remaining = cli.parse_known_args(args)
        
    if parsed.help:
        SystemExit(run_help(sys.executable))
        
    if parsed.mod:
        module = parsed.mod[0]
        module_args = parsed.mod[1:]
        if module in _AVAILABLE_MODULES:
            SystemExit(handle_custom_module(module, module_args))
    
    SystemExit(run_cmd(sys.executable, *args))

if __name__=="__main__":
    main()
    