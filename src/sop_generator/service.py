import base64
import binascii

from fastapi import FastAPI
from fastapi import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .drafting import draft_sop
from .models import CaptureEvent, CaptureSession, DraftSop
from .paths import SopPaths
from .storage import SessionStore


class SessionCreateRequest(BaseModel):
    title: str


class ScreenshotUploadRequest(BaseModel):
    filename: str
    screenshot_base64: str


def create_app(paths: SopPaths | None = None) -> FastAPI:
    app = FastAPI(title="MTG SOP Generator Companion API")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )
    store = SessionStore(paths or SopPaths.default())

    def ensure_session_exists(session_id: str) -> CaptureSession:
        try:
            return store.read_session(session_id)
        except FileNotFoundError as exc:
            raise HTTPException(status_code=404, detail="Session not found") from exc
        except ValueError as exc:
            raise HTTPException(status_code=400, detail="Invalid session ID") from exc

    @app.get("/health")
    def health() -> dict[str, bool]:
        return {"ok": True}

    @app.post("/api/sessions")
    def create_session(request: SessionCreateRequest) -> CaptureSession:
        return store.create_session(request.title)

    @app.post("/api/sessions/{session_id}/events")
    def append_event(session_id: str, event: CaptureEvent) -> dict[str, bool]:
        ensure_session_exists(session_id)
        store.append_event(session_id, event)
        return {"ok": True}

    @app.post("/api/sessions/{session_id}/draft")
    def draft_session(session_id: str) -> DraftSop:
        session = ensure_session_exists(session_id)
        events = store.read_events(session_id)
        draft = draft_sop(session.title, events, store.paths.house_style)
        store.write_draft(session_id, draft)
        return draft

    @app.post("/api/sessions/{session_id}/screenshots")
    def upload_screenshot(
        session_id: str,
        request: ScreenshotUploadRequest,
    ) -> dict[str, str]:
        ensure_session_exists(session_id)
        try:
            base64.b64decode(request.screenshot_base64, validate=True)
        except binascii.Error as exc:
            raise HTTPException(status_code=400, detail="Invalid screenshot_base64") from exc
        path = store.write_screenshot(
            session_id=session_id,
            screenshot_base64=request.screenshot_base64,
            filename=request.filename,
        )
        return {"path": str(path)}

    return app
