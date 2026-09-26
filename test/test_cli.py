import os
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def run_cli(working_dir: Path, *arguments: str) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    source_dir = str(PROJECT_ROOT / "src")
    existing_pythonpath = env.get("PYTHONPATH")
    env["PYTHONPATH"] = os.pathsep.join(
        path for path in (source_dir, existing_pythonpath) if path
    )
    env["COFE_DATA_DIR"] = str(working_dir / ".cenv")

    return subprocess.run(
        [sys.executable, "-m", "cofe", *map(str, arguments)],
        cwd=working_dir,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )


def test_cli_help(tmp_path: Path) -> None:
    result = run_cli(tmp_path, "--help")

    assert result.returncode == 0
    assert "usage:" in result.stdout.lower()
    assert "exec" in result.stdout
    assert "config" in result.stdout


def test_cli_config_list(tmp_path: Path) -> None:
    result = run_cli(tmp_path, "config", "list")

    assert result.returncode == 0
    assert "[env]" in result.stdout
    assert "[available]" in result.stdout
    assert "[active]" in result.stdout


def test_cli_exec_python_file_forwards_arguments(tmp_path: Path) -> None:
    script = tmp_path / "script.py"
    script.write_text(
        "import sys\nprint('|'.join(sys.argv[1:]))\n",
        encoding="utf-8",
    )

    result = run_cli(tmp_path, "exec", script, "first", "second")

    assert result.returncode == 0
    assert result.stdout.strip() == "first|second"


def test_cli_exec_y_file_imports_python_module(tmp_path: Path) -> None:
    helper = tmp_path / "helper.py"
    helper.write_text("VALUE = 'loaded'\n", encoding="utf-8")
    script = tmp_path / "script.y"
    script.write_text(
        "from helper import VALUE\nprint(VALUE)\n",
        encoding="utf-8",
    )

    result = run_cli(tmp_path, "exec", script)

    assert result.returncode == 0
    assert result.stdout.strip() == "loaded"