import subprocess
import sys
from pathlib import Path

from typer.testing import CliRunner

from sop_generator.cli import app


def test_cli_help_loads():
    result = CliRunner().invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "SOP Generator" in result.output
    assert "serve" in result.output


def test_repo_root_import_resolves_cli_submodule():
    repo_root = Path(__file__).resolve().parents[1]
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            "from sop_generator.cli import app; print(app.info.help)",
        ],
        cwd=repo_root,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "SOP Generator: browser workflow capture and Halo KB publishing." in result.stdout
