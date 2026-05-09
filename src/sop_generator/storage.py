import base64
from pathlib import Path

from .models import CaptureEvent, CaptureSession, DraftSop
from .paths import SopPaths


def _is_relative_to(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


class SessionStore:
    def __init__(self, paths: SopPaths):
        self.paths = paths.ensure()

    def create_session(self, title: str) -> CaptureSession:
        session = CaptureSession(title=title)
        return self.write_session(session)

    def session_dir(self, session_id: str) -> Path:
        if "/" in session_id or "\\" in session_id:
            raise ValueError(f"Unsafe session ID: {session_id!r}")
        root = self.paths.sessions.resolve()
        candidate = (root / session_id).resolve()
        if not _is_relative_to(candidate, root):
            raise ValueError(f"Unsafe session ID: {session_id!r}")
        return candidate

    def write_session(self, session: CaptureSession) -> CaptureSession:
        path = self.session_dir(session.id)
        path.mkdir(parents=True, exist_ok=True)
        (path / "metadata.json").write_text(session.model_dump_json(), encoding="utf-8")
        return session

    def read_session(self, session_id: str) -> CaptureSession:
        path = self.session_dir(session_id) / "metadata.json"
        return CaptureSession.model_validate_json(path.read_text(encoding="utf-8"))

    def append_event(self, session_id: str, event: CaptureEvent) -> None:
        path = self.session_dir(session_id)
        path.mkdir(parents=True, exist_ok=True)
        with (path / "events.jsonl").open("a", encoding="utf-8") as stream:
            stream.write(event.model_dump_json())
            stream.write("\n")

    def read_events(self, session_id: str) -> list[CaptureEvent]:
        path = self.session_dir(session_id) / "events.jsonl"
        if not path.exists():
            return []
        return [
            CaptureEvent.model_validate_json(line)
            for line in path.read_text(encoding="utf-8").splitlines()
            if line
        ]

    def write_screenshot(self, session_id: str, screenshot_base64: str, filename: str) -> Path:
        path = self.session_dir(session_id) / "screenshots"
        path.mkdir(parents=True, exist_ok=True)
        screenshot_path = path / Path(filename).name
        screenshot_path.write_bytes(base64.b64decode(screenshot_base64))
        return screenshot_path

    def write_draft(self, session_id: str, draft: DraftSop) -> Path:
        path = self.session_dir(session_id)
        path.mkdir(parents=True, exist_ok=True)
        draft_path = path / "draft.json"
        draft_path.write_text(draft.model_dump_json(), encoding="utf-8")
        return draft_path

    def read_draft(self, session_id: str) -> DraftSop:
        path = self.session_dir(session_id) / "draft.json"
        return DraftSop.model_validate_json(path.read_text(encoding="utf-8"))
