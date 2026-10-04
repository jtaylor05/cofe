import argparse
import subprocess
import sys

from importlib.metadata import version

from cofe.cli.config import main as config_main
from cofe.cli.exec import main as exec_main
from cofe.cli.transform import main as transform_main

_AVAILABLE_MODULES = {"config", "transform", "exec"}


def get_cli():
    parser = argparse.ArgumentParser(
        prog="cofe",
        description="A CounterFactual Environment python interpreter; completely compatible with standard python.",
        add_help=False,
    )
    parser.add_argument("-v", "--version", action="version", version=f"cofe {version('cofe')}")
    parser.add_argument("-h", "--help", action="store_true")
    parser.add_argument("-m", "--module", dest="mod", nargs=argparse.REMAINDER, type=str)
    return parser

def run_help(executable: str, new_name: str = "cofe") -> None:
    out = subprocess.run([executable, "-h"], capture_output=True, text=True).stdout
    out = out.replace(f"usage: {executable}", f"usage: {new_name}")
    print(out)

def handle_custom_module(module: str, args=None):
    args = [] if args is None else list(args)

    match module:
        case "config":
            return config_main(args)
        case "exec":
            return exec_main(args)
        case "transform":
            return transform_main(args)
        case _:
            raise ValueError(f"Unknown module: {module!r}")


def main(argv=None):
    args = list(sys.argv[1:] if argv is None else argv)
    cli = get_cli()
    parsed, remaining = cli.parse_known_args(args)

    if parsed.help:
        run_help(sys.executable)
        return 0

    if parsed.mod:
        module = parsed.mod[0]
        module_args = parsed.mod[1:]
        if module in _AVAILABLE_MODULES:
            return handle_custom_module(module, module_args)
        remaining.extend(["-m", module, *module_args])

    if remaining and remaining[0] in _AVAILABLE_MODULES:
        return handle_custom_module(remaining[0], remaining[1:])

    run_help(sys.executable)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
