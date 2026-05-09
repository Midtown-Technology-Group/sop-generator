from collections.abc import Iterable

from .models import CaptureEvent, SopStep


IGNORED_EVENT_TYPES = {"form_change", "pause", "resume"}


def build_steps(events: Iterable[CaptureEvent]) -> list[SopStep]:
    steps: list[SopStep] = []
    for event in events:
        action = _event_action(event)
        if action is None:
            continue
        steps.append(
            SopStep(
                order=len(steps) + 1,
                action=action,
                evidence=[event.screenshot_path] if event.screenshot_path else [],
            )
        )
    return steps


def _event_action(event: CaptureEvent) -> str | None:
    if event.type in IGNORED_EVENT_TYPES:
        return None
    if event.type == "navigation":
        target = event.title or event.url
        if not target:
            return None
        return f"Open {target}."
    if event.type == "click":
        return f"Select {event.label or 'the highlighted control'}."
    if event.type == "submit":
        return f"Submit {event.label or 'the form'}."
    if event.type == "note":
        return event.note
    return None
