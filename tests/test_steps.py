from sop_generator.models import CaptureEvent
from sop_generator.steps import build_steps


def test_build_steps_keeps_meaningful_events():
    events = [
        CaptureEvent(type="navigation", title="Admin Portal", url="https://portal.test"),
        CaptureEvent(type="form_change", label="Password", value_hint="changed"),
        CaptureEvent(type="click", label="Users"),
        CaptureEvent(type="submit", label="Save"),
    ]
    steps = build_steps(events)
    assert [step.action for step in steps] == [
        "Open Admin Portal.",
        "Select Users.",
        "Submit Save.",
    ]


def test_build_steps_attaches_screenshot_evidence():
    steps = build_steps([CaptureEvent(type="click", label="Users", screenshot_path="shot.png")])
    assert steps[0].evidence == ["shot.png"]
