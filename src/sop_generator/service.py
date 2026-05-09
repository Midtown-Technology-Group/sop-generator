from fastapi import FastAPI
from pydantic import BaseModel

from .models import CaptureEvent, CaptureSession
from .paths import SopPaths
from .storage import SessionStore


class SessionCreateRequest(BaseModel):
    title: str


class ScreenshotUploadRequest(BaseModel):
    filename: str
    screenshot_base64: str


def create_app(paths: SopPaths | None = None) -> FastAPI:
    app = FastAPI(title="MTG SOP Generator Companion API")
    store = SessionStore(paths or SopPaths.default())

    @app.get("/health")
    def health() -> dict[str, bool]:
        return {"ok": True}

    @app.post("/api/sessions")
    def create_session(request: SessionCreateRequest) -> CaptureSession:
        return store.create_session(request.title)

    @app.post("/api/sessions/{session_id}/events")
    def append_event(session_id: str, event: CaptureEvent) -> dict[str, bool]:
        store.append_event(session_id, event)
        return {"ok": True}

    @app.post("/api/sessions/{session_id}/screenshots")
    def upload_screenshot(
        session_id: str,
        request: ScreenshotUploadRequest,
    ) -> dict[str, str]:
        path = store.write_screenshot(
            session_id=session_id,
            screenshot_base64=request.screenshot_base64,
            filename=request.filename,
        )
        return {"path": str(path)}

    return app
