from dataclasses import FrozenInstanceError

import pytest

from sop_generator.paths import SopPaths


def test_default_paths_use_local_appdata(monkeypatch, tmp_path):
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    paths = SopPaths.default()
    assert paths.root == tmp_path / "MTG" / "SOPGenerator"
    assert paths.sessions == paths.root / "sessions"
    assert paths.house_style == paths.root / "house-style.md"


def test_default_paths_fall_back_to_local_share(monkeypatch, tmp_path):
    monkeypatch.delenv("LOCALAPPDATA", raising=False)
    monkeypatch.setattr("pathlib.Path.home", lambda: tmp_path)
    paths = SopPaths.default()
    assert paths.root == tmp_path / ".local" / "share" / "MTG" / "SOPGenerator"
    assert paths.sessions == paths.root / "sessions"
    assert paths.house_style == paths.root / "house-style.md"


def test_default_paths_fall_back_when_local_appdata_is_empty(monkeypatch, tmp_path):
    monkeypatch.setenv("LOCALAPPDATA", "")
    monkeypatch.setattr("pathlib.Path.home", lambda: tmp_path)
    paths = SopPaths.default()
    assert paths.root == tmp_path / ".local" / "share" / "MTG" / "SOPGenerator"
    assert paths.sessions == paths.root / "sessions"
    assert paths.house_style == paths.root / "house-style.md"


def test_ensure_creates_sessions_directory_and_returns_self(monkeypatch, tmp_path):
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    paths = SopPaths.default()
    ensured = paths.ensure()
    assert ensured is paths
    assert paths.sessions.is_dir()


def test_ensure_default_style_writes_local_guidance(monkeypatch, tmp_path):
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    paths = SopPaths.default()
    written = paths.ensure_default_style()
    text = written.read_text(encoding="utf-8")
    assert "MTG technicians" in text
    assert "Do not include raw passwords" in text


def test_ensure_default_style_preserves_existing_content(monkeypatch, tmp_path):
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    paths = SopPaths.default()
    paths.ensure()
    paths.house_style.write_text("custom house style", encoding="utf-8")
    written = paths.ensure_default_style()
    assert written == paths.house_style
    assert written.read_text(encoding="utf-8") == "custom house style"


def test_paths_are_frozen(monkeypatch, tmp_path):
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    paths = SopPaths.default()
    with pytest.raises(FrozenInstanceError):
        paths.root = tmp_path
