from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_readme_documents_local_capture_boundary():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "%LOCALAPPDATA%\\MTG\\SOPGenerator" in readme
    assert "house-style.md" in readme
    assert "style\\" not in readme
    assert "Halo KB" in readme
    assert "Bifrost" in readme
    assert "clicks, navigation, form changes with value hints, and form submits" in readme
    assert "does not provide operator note or screenshot controls" in readme
    assert "python -m sop_generator draft <session-id>" in readme
    assert "python -m sop_generator export <session-id>" in readme
    assert "BIFROST_URL" in readme
    assert "BIFROST_TOKEN" in readme
    assert "publish does not enforce an approval gate in code" in readme


def test_quickstart_mentions_browser_extension():
    quickstart = (ROOT / "QUICKSTART.md").read_text(encoding="utf-8")
    assert "extension/browser" in quickstart
    assert "python -m sop_generator serve" in quickstart
    assert "python -m sop_generator draft <session-id>" in quickstart
    assert "python -m sop_generator export <session-id>" in quickstart
    assert "python -m sop_generator publish <session-id>" in quickstart
    assert "BIFROST_URL" in quickstart
    assert "BIFROST_TOKEN" in quickstart
    assert "manual review" in quickstart
    assert "notes or screenshots" not in quickstart


def test_launcher_stops_when_init_style_fails():
    launcher = (ROOT / "Start-SOPGenerator.ps1").read_text(encoding="utf-8")
    assert "if ($LASTEXITCODE -ne 0)" in launcher
    assert "exit $LASTEXITCODE" in launcher
