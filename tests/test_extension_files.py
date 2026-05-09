import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_manifest_declares_localhost_permission():
    manifest = json.loads((ROOT / "extension/browser/manifest.json").read_text(encoding="utf-8"))
    assert manifest["manifest_version"] == 3
    assert "http://127.0.0.1:8765/*" in manifest["host_permissions"]
    assert "storage" in manifest["permissions"]


def test_popup_has_visible_recording_controls():
    popup = (ROOT / "extension/browser/popup.html").read_text(encoding="utf-8")
    assert "Start" in popup
    assert "Pause" in popup
    assert "Stop" in popup
