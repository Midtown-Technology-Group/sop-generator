from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_readme_documents_local_capture_boundary():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "%LOCALAPPDATA%\\MTG\\SOPGenerator" in readme
    assert "Halo KB" in readme
    assert "Bifrost" in readme


def test_quickstart_mentions_browser_extension():
    quickstart = (ROOT / "QUICKSTART.md").read_text(encoding="utf-8")
    assert "extension/browser" in quickstart
    assert "python -m sop_generator serve" in quickstart
