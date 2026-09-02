import subprocess
import sys
from pathlib import Path


def test_tokenizer_creates_tokenized_file(tmp_path):
    source = tmp_path / "sample.py"
    source.write_text("print('hello')\n", encoding="utf-8")

    repo_root = Path(__file__).resolve().parents[1]
    result = subprocess.run(
        [sys.executable, "tokenizer.py", str(source)],
        cwd=repo_root,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    output = tmp_path / "sample_tokenized.py"
    assert output.exists(), "tokenized output file was not created"
    contents = output.read_text(encoding="utf-8")
    assert "TokenInfo" in contents
    assert "print" in contents
