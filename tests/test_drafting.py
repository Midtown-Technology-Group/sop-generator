from sop_generator.drafting import draft_sop
from sop_generator.models import CaptureEvent


def test_draft_sop_uses_style_file(tmp_path):
    style = tmp_path / "house-style.md"
    style.write_text("Do not include raw passwords.", encoding="utf-8")
    draft = draft_sop("Reset MFA", [CaptureEvent(type="click", label="Reset MFA")], style)
    assert draft.title == "Reset MFA"
    assert draft.steps[0].action == "Select Reset MFA."
    assert any("secret" in warning.lower() for warning in draft.warnings)


def test_draft_sop_uses_capture_summary(tmp_path):
    draft = draft_sop("Reset MFA", [], tmp_path / "missing-style.md")
    assert draft.summary == "Procedure captured from a browser workflow recording."
