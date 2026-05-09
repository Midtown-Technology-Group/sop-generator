from sop_generator.models import CaptureEvent, CaptureSession, DraftSop, SopStep


def test_capture_session_defaults():
    session = CaptureSession(title="New SOP")
    assert session.title == "New SOP"
    assert session.status == "recording"
    assert session.id


def test_capture_event_requires_known_type():
    event = CaptureEvent(type="navigation", url="https://example.test", title="Example")
    assert event.type == "navigation"
    assert event.url == "https://example.test"


def test_draft_sop_contains_steps():
    step = SopStep(order=1, action="Open the customer portal", evidence=["screenshots/1.png"])
    draft = DraftSop(title="Reset MFA", summary="Reset a user's MFA.", steps=[step])
    assert draft.steps[0].order == 1
