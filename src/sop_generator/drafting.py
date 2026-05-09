from collections.abc import Iterable
from pathlib import Path

from .models import CaptureEvent, DraftSop
from .steps import build_steps

CAPTURE_SUMMARY = "Procedure captured from a browser workflow recording."
SECRET_REVIEW_WARNING = "Review screenshots and remove any visible secrets before publishing."
SENSITIVE_STYLE_TERMS = ("password", "secret", "token")


def draft_sop(title: str, events: Iterable[CaptureEvent], style_file: Path) -> DraftSop:
    style = style_file.read_text(encoding="utf-8") if style_file.exists() else ""
    warnings = []
    if any(term in style.lower() for term in SENSITIVE_STYLE_TERMS):
        warnings.append(SECRET_REVIEW_WARNING)
    return DraftSop(
        title=title,
        summary=CAPTURE_SUMMARY,
        steps=build_steps(events),
        warnings=warnings,
    )
