import subprocess
import sys
from pathlib import Path

from typer.testing import CliRunner

from sop_generator.cli import app
from sop_generator.models import CaptureEvent
from sop_generator.paths import SopPaths
from sop_generator.storage import SessionStore


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


def test_cli_draft_unknown_session_has_useful_message(tmp_path, monkeypatch):
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))

    result = CliRunner().invoke(app, ["draft", "not-created"])

    assert result.exit_code != 0
    assert "Session not found: not-created" in result.output


def test_cli_draft_writes_draft_path(tmp_path, monkeypatch):
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    store = SessionStore(SopPaths.default())
    session = store.create_session("Reset MFA")
    store.append_event(session.id, CaptureEvent(type="click", label="Reset MFA"))

    result = CliRunner().invoke(app, ["draft", session.id])

    assert result.exit_code == 0
    assert result.output.strip().endswith("draft.json")
    assert store.read_draft(session.id).steps[0].action == "Select Reset MFA."
