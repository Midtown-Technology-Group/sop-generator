import pytest

from sop_generator.models import CaptureEvent, DraftSop, SopStep
from sop_generator.paths import SopPaths
from sop_generator.render_halo import render_halo_html
from sop_generator.storage import SessionStore


@pytest.mark.parametrize("separator", ["\u0085", "\u2028", "\u2029", "\v", "\f"])
def test_event_jsonl_round_trip_preserves_unicode_separators(tmp_path, separator):
    store = SessionStore(SopPaths(tmp_path, tmp_path / "sessions", tmp_path / "style.md"))
    session = store.create_session("Synthetic Unicode capture")
    event = CaptureEvent(type="note", note=f"before{separator}after")
    store.append_event(session.id, event)
    store.append_event(session.id, CaptureEvent(type="stop"))

    events = store.read_events(session.id)

    assert events[0] == event
    assert len(events) == 2


@pytest.mark.parametrize(
    "source",
    [
        "javascript:alert(1)",
        "data:image/svg+xml,<svg onload='alert(1)'/>",
        "vbscript:msgbox(1)",
        "JaVaScRiPt:alert(1)",
        "java\nscript:alert(1)",
    ],
)
def test_render_rejects_active_evidence_sources(source):
    draft = DraftSop(
        title="Synthetic",
        summary="Review",
        steps=[
            SopStep(order=1, action="Open", evidence=[source]),
        ],
    )

    with pytest.raises(ValueError, match="Unsafe evidence"):
        render_halo_html(draft)


def test_imported_crlf_jsonl_preserves_unicode_and_blank_records(tmp_path):
    store = SessionStore(SopPaths(tmp_path, tmp_path / "sessions", tmp_path / "style.md"))
    session = store.create_session("Synthetic import")
    event = CaptureEvent(type="click", label="Line\u2028two", title="Page\u0085title")
    path = store.session_dir(session.id) / "events.jsonl"
    path.write_bytes((event.model_dump_json() + "\r\n\r\n").encode("utf-8"))

    assert store.read_events(session.id) == [event]


@pytest.mark.parametrize(
    "source",
    [
        "screenshots/one.png",
        "/tmp/synthetic/one.png",
        r"C:\captures\one.png",
        "file:///C:/captures/one.png",
        "https://example.test/one.png?a=1&b=2",
        "http://example.test/one.png",
        'screenshots/one" onerror="alert(1).png',
    ],
)
def test_render_safe_sources_are_escaped_and_deterministic(source):
    from html import escape

    draft = DraftSop(
        title="<Title>",
        summary="<Summary>",
        warnings=["<Warning>"],
        steps=[
            SopStep(order=2, action="Second", evidence=[source], expected_result="<Result>"),
            SopStep(order=1, action="<First>"),
        ],
    )
    original = draft.model_dump_json()

    html = render_halo_html(draft)

    assert html == render_halo_html(draft)
    assert draft.model_dump_json() == original
    assert html.index("&lt;First&gt;") < html.index("Second")
    assert f'src="{escape(source, quote=True)}"' in html
    for text in ("Title", "Summary", "Warning", "Result"):
        assert f"&lt;{text}&gt;" in html
