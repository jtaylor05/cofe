import argparse

def get_cli():
    parser = argparse.ArgumentParser(prog="cofe-transform", description="Module to transform python files in the current cofe environment.")
    
    cmd_subparsers = parser.add_subparsers(title="op", dest="cmd")
    
    from_parser = cmd_subparsers.add_parser("from", help="Transform a file to another file.")
    from_parser.add_argument("source", type=str, help="Python or cofe environment file.")
    from_parser.add_argument("--to", type=str, required=True, help="Output file path. If not provided, will print to stdout.")
    from_parser.add_argument("-c", "--config", type=str, help="Path to a config file to use for the transformation. If not provided, will use the current environment config.")
    
    return parser

def main(args):
    parser = get_cli()
    parsed = parser.parse_args(args)
    
    if parsed.cmd:
        match parsed.cmd:
            case "from":
                pass
    
    