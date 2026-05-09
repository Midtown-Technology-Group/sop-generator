from sop_generator.paths import SopPaths


def test_default_paths_use_local_appdata(monkeypatch, tmp_path):
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    paths = SopPaths.default()
    assert paths.root == tmp_path / "MTG" / "SOPGenerator"
    assert paths.sessions == paths.root / "sessions"
    assert paths.house_style == paths.root / "house-style.md"


def test_ensure_default_style_writes_local_guidance(monkeypatch, tmp_path):
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    paths = SopPaths.default()
    written = paths.ensure_default_style()
    text = written.read_text(encoding="utf-8")
    assert "MTG technicians" in text
    assert "Do not include raw passwords" in text
