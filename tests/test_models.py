from datetime import datetime, timezone
from typing import get_args

import pytest
from pydantic import ValidationError

from sop_generator.models import (
    CaptureEvent,
    CaptureSession,
    DraftSop,
    EventType,
    PublishResult,
    SopStep,
    utc_now,
)


def test_capture_session_defaults():
    session = CaptureSession(title="New SOP")
    assert session.title == "New SOP"
    assert session.status == "recording"
    assert session.id


def test_capture_event_requires_known_type():
    event = CaptureEvent(type="navigation", url="https://example.test", title="Example")
    assert event.type == "navigation"
    assert event.url == "https://example.test"


def test_all_capture_event_types_are_accepted():
    assert set(get_args(EventType)) == {
        "click",
        "navigation",
        "form_change",
        "submit",
        "note",
        "screenshot",
        "pause",
        "resume",
        "stop",
    }

    for event_type in get_args(EventType):
        assert CaptureEvent(type=event_type).type == event_type


def test_unknown_capture_event_type_is_rejected():
    with pytest.raises(ValidationError):
        CaptureEvent(type="unknown")


def test_default_datetimes_are_utc_aware():
    now = utc_now()
    session = CaptureSession(title="New SOP")
    event = CaptureEvent(type="navigation")

    assert now.tzinfo is timezone.utc
    assert session.created_at.tzinfo is timezone.utc
    assert session.updated_at.tzinfo is timezone.utc
    assert event.timestamp.tzinfo is timezone.utc


def test_capture_event_rejects_naive_timestamp():
    with pytest.raises(ValidationError):
        CaptureEvent(type="navigation", timestamp=datetime(2026, 5, 9, 12, 0, 0))


def test_capture_session_rejects_naive_created_at():
    with pytest.raises(ValidationError):
        CaptureSession(title="New SOP", created_at=datetime(2026, 5, 9, 12, 0, 0))


def test_capture_session_rejects_naive_updated_at():
    with pytest.raises(ValidationError):
        CaptureSession(title="New SOP", updated_at=datetime(2026, 5, 9, 12, 0, 0))


def test_draft_sop_contains_steps():
    step = SopStep(order=1, action="Open the customer portal", evidence=["screenshots/1.png"])
    draft = DraftSop(title="Reset MFA", summary="Reset a user's MFA.", steps=[step])
    assert draft.steps[0].order == 1


def test_sop_step_evidence_lists_are_independent():
    first = SopStep(order=1, action="Open the customer portal")
    second = SopStep(order=2, action="Find the user")

    first.evidence.append("screenshots/1.png")

    assert second.evidence == []


def test_draft_sop_warning_lists_are_independent():
    first = DraftSop(title="Reset MFA", summary="Reset a user's MFA.", steps=[])
    second = DraftSop(title="Disable user", summary="Disable a user account.", steps=[])

    first.warnings.append("Review sensitive customer identifiers.")

    assert second.warnings == []


def test_publish_result_defaults_and_fields():
    result = PublishResult(ok=True, kb_article_id="KB123", url="https://halo.example/kb/123")

    assert result.ok is True
    assert result.kb_article_id == "KB123"
    assert result.url == "https://halo.example/kb/123"
    assert result.message is None
