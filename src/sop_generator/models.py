from datetime import datetime, timezone
from typing import Literal
from uuid import uuid4

from pydantic import AwareDatetime, BaseModel, Field

EventType = Literal[
    "click",
    "navigation",
    "form_change",
    "submit",
    "note",
    "screenshot",
    "pause",
    "resume",
    "stop",
]


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class CaptureSession(BaseModel):
    id: str = Field(default_factory=lambda: uuid4().hex)
    title: str
    status: Literal["recording", "paused", "stopped"] = "recording"
    created_at: AwareDatetime = Field(default_factory=utc_now)
    updated_at: AwareDatetime = Field(default_factory=utc_now)


class CaptureEvent(BaseModel):
    type: EventType
    timestamp: AwareDatetime = Field(default_factory=utc_now)
    url: str | None = None
    title: str | None = None
    label: str | None = None
    selector: str | None = None
    value_hint: str | None = None
    screenshot_path: str | None = None
    note: str | None = None


class SopStep(BaseModel):
    order: int
    action: str
    expected_result: str | None = None
    evidence: list[str] = Field(default_factory=list)


class DraftSop(BaseModel):
    title: str
    summary: str
    steps: list[SopStep]
    warnings: list[str] = Field(default_factory=list)


class PublishResult(BaseModel):
    ok: bool
    kb_article_id: str | None = None
    url: str | None = None
    message: str | None = None
