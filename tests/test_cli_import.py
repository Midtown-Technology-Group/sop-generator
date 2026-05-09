from typer.testing import CliRunner

from sop_generator.cli import app


def test_cli_help_loads():
    result = CliRunner().invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "SOP Generator" in result.output
    assert "serve" in result.output
