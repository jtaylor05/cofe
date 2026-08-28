import sys

import argparse as ap

from . import PythonLauncher, YthonConfigParser, install_import_hook

def config_command(raw_changes: list[str]):
    print("changes:", raw_changes)
    changes = {d[0]:d[1] for d in [c.split('=') for c in raw_changes]}
    
    config = YthonConfigParser
    for k,v in changes.items():
        config.set(k, v)
    
    config.write()

def exec_command(file_path: str, remainder: list[str]):
    sys.argv = [file_path] + remainder
    print(sys.argv)
    
    install_import_hook()
    
    launcher = PythonLauncher(file_path)
    launcher.launch()

if __name__ == "__main__":
    parser = ap.ArgumentParser(
        prog="ython",
        description="A counterfactual python interpreter; completely compatible with standard python.",
        epilog="This project is under development. There may still be bugs."
    )
    subparsers = parser.add_subparsers(dest="command", required=True, help="Which submodule to use.")
    
    config_parser = subparsers.add_parser("config", help="configure interpreter settings and modules.")
    config_parser.add_argument("-c", "--change", nargs='*', type=str, help="Changes made to current configuration.")
    
    exec_parser = subparsers.add_parser("exec", help="acts as an entry point into module code.")
    exec_parser.add_argument("file_path", type=str)
    
    args, remainder = parser.parse_known_args()
    
    match args.command:
        case "config":
            config_command(args.change)
            
        case "exec":
            exec_command(args.file_path, remainder)
            
            