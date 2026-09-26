import os
import subprocess
import sys


COMMANDS = [
    ["cofe", "-h"],
    ["cofe", "config", "list"]
]


def run_command(command):
    print(f"\n$ {' '.join(command)}")
    try:
        result = subprocess.run(command, capture_output=True, text=True)
    except FileNotFoundError:
        print(f"Command not found: {command[0]}", file=sys.stderr)
        return 1

    if result.stdout:
        print(result.stdout, end="")

    if result.stderr:
        print(result.stderr, end="", file=sys.stderr)

    if result.returncode != 0:
        print(f"\nCommand exited with code {result.returncode}", file=sys.stderr)

    return result.returncode

def test_add():
    cmd = ["cofe", "config", "add"]
