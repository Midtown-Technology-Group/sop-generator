import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_manifest_declares_localhost_permission():
    manifest = json.loads((ROOT / "extension/browser/manifest.json").read_text(encoding="utf-8"))
    assert manifest["manifest_version"] == 3
    assert "http://127.0.0.1:8765/*" in manifest["host_permissions"]
    # Task 9 intentionally keeps the broad MV3 permissions and <all_urls> match from the plan.
    assert sorted(manifest["permissions"]) == ["activeTab", "scripting", "storage", "tabs"]


def test_manifest_declares_background_content_and_popup_mappings():
    manifest = json.loads((ROOT / "extension/browser/manifest.json").read_text(encoding="utf-8"))
    assert manifest["background"]["service_worker"] == "background.js"
    assert manifest["content_scripts"][0]["matches"] == ["<all_urls>"]
    assert manifest["content_scripts"][0]["js"] == ["content.js"]
    assert manifest["action"]["default_popup"] == "popup.html"


def test_popup_has_visible_recording_controls():
    popup = (ROOT / "extension/browser/popup.html").read_text(encoding="utf-8")
    assert "Start" in popup
    assert "Pause" in popup
    assert "Resume" in popup
    assert "Stop" in popup


def test_background_posts_sessions_events_and_preserves_state_on_lifecycle_failure():
    background = (ROOT / "extension/browser/background.js").read_text(encoding="utf-8")
    assert 'fetch(`${API_BASE}/api/sessions`' in background
    assert 'fetch(`${API_BASE}/api/sessions/${state.sessionId}/events`' in background
    assert "chrome.tabs.onUpdated.addListener" in background
    assert 'message.type === "capture-event"' in background
    assert "throw new Error(`Event append failed:" in background
    assert 'appendEvent({ type: "pause"' in background
    assert 'appendEvent({ type: "stop"' in background
    assert ".catch(() => null)" not in background
    assert "ignorePaused" in background
    assert 'appendEvent({ type: "stop", note: "Recording stopped" }, { ignorePaused: true })' in background


def test_content_posts_meaningful_events_without_raw_input_values():
    content = (ROOT / "extension/browser/content.js").read_text(encoding="utf-8")
    assert 'type: "click"' in content
    assert "label: visibleLabel(target)" in content
    assert "url: window.location.href" in content
    assert "title: document.title" in content
    assert 'type: "submit"' in content
    assert "label: formLabel(event.target)" in content
    assert 'type: "form_change"' in content
    assert "label: fieldLabel(target)" in content
    assert 'value_hint: "changed"' in content
    assert "target.value" not in content
    assert "value:" not in content


def test_popup_wires_lifecycle_controls_and_surfaces_errors():
    popup = (ROOT / "extension/browser/popup.js").read_text(encoding="utf-8")
    assert 'send("start"' in popup
    assert 'send("pause")' in popup
    assert 'send("resume")' in popup
    assert 'send("stop")' in popup
    assert "setMessage(error.message, true)" in popup
    assert 'response.ok === false' in popup
