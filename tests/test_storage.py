import base64

from sop_generator.models import CaptureEvent
from sop_generator.paths import SopPaths
from sop_generator.storage import SessionStore


def make_store(tmp_path):
    return SessionStore(
        SopPaths(
            root=tmp_path,
            sessions=tmp_path / "sessions",
            house_style=tmp_path / "house-style.md",
        )
    )


def test_create_session_writes_metadata(tmp_path):
    store = make_store(tmp_path)
    session = store.create_session("Customer onboarding")
    loaded = store.read_session(session.id)
    assert loaded.title == "Customer onboarding"


def test_append_and_read_events(tmp_path):
    store = make_store(tmp_path)
    session = store.create_session("Reset MFA")
    store.append_event(session.id, CaptureEvent(type="navigation", url="https://portal.test"))
    events = store.read_events(session.id)
    assert events[0].type == "navigation"


def test_write_screenshot_from_base64(tmp_path):
    store = make_store(tmp_path)
    session = store.create_session("Screenshot")
    encoded = base64.b64encode(b"png-bytes").decode("ascii")
    path = store.write_screenshot(session.id, encoded, "capture.png")
    assert path.name == "capture.png"
    assert path.read_bytes() == b"png-bytes"
