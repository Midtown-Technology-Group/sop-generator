# Browser Capture Halo Publishing Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the v1 browser-first SOP capture system: local full-fidelity capture storage, browser extension ingestion, automatic SOP drafting, review/export flow, and a Bifrost Halo publish contract.

**Architecture:** Convert the legacy single-script Greenshot watcher into a small Python package with focused modules. The companion service owns local session storage, event ingestion, draft generation, Halo HTML rendering, and Bifrost publishing. A thin Manifest V3 browser extension captures meaningful browser events and posts them to localhost.

**Tech Stack:** Python 3.10+, FastAPI/Uvicorn, Pydantic, Typer, pytest, httpx, vanilla Manifest V3 browser extension JavaScript, local JSON/JSONL/filesystem storage under `%LOCALAPPDATA%\MTG\SOPGenerator`.

---

## File Structure

Create a package while keeping the root script as a compatibility wrapper.

```text
src/sop_generator/
  __init__.py              Package metadata.
  __main__.py              Enables python -m sop_generator.
  cli.py                   Typer CLI for init-style, serve, draft, export, publish.
  paths.py                 Machine-local path and house-style bootstrap helpers.
  models.py                Pydantic session, event, draft, and publish models.
  storage.py               Filesystem session store with JSON metadata and JSONL events.
  steps.py                 Converts noisy capture events into operator-facing SOP steps.
  drafting.py              Builds DraftSop objects from events, screenshots, and style text.
  render_halo.py           Renders reviewed drafts into Halo-safe HTML.
  publish_bifrost.py       Bifrost client contract for Halo KB publishing.
  service.py               FastAPI local companion API.
  legacy_greenshot.py      Preserves the old screenshot watcher path behind an explicit command.
extension/browser/
  manifest.json            Manifest V3 extension declaration.
  background.js            Recording state, local API client, tab navigation capture.
  content.js               Meaningful click, submit, and form interaction capture.
  popup.html               Visible recorder controls.
  popup.js                 Starts, pauses, resumes, stops sessions.
  styles.css               Small dark popup UI.
tests/
  test_cli_import.py
  test_paths.py
  test_models.py
  test_storage.py
  test_steps.py
  test_drafting.py
  test_render_halo.py
  test_publish_bifrost.py
  test_service.py
  test_extension_files.py
  test_end_to_end.py
```

## Task 1: Package Skeleton and CLI

**Files:**
- Create: `pyproject.toml`
- Create: `src/sop_generator/__init__.py`
- Create: `src/sop_generator/__main__.py`
- Create: `src/sop_generator/cli.py`
- Modify: `sop_generator.py`
- Test: `tests/test_cli_import.py`

- [ ] **Step 1: Write the failing CLI import test**

```python
from typer.testing import CliRunner

from sop_generator.cli import app


def test_cli_help_loads():
    result = CliRunner().invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "SOP Generator" in result.output
    assert "serve" in result.output
```

- [ ] **Step 2: Run the test and confirm the package does not exist yet**

Run: `python -m pytest tests/test_cli_import.py -q`

Expected: `ModuleNotFoundError: No module named 'sop_generator'`

- [ ] **Step 3: Add packaging and the minimal CLI**

`pyproject.toml`:

```toml
[build-system]
requires = ["setuptools>=68", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "mtg-sop-generator"
version = "0.1.0"
description = "Local browser workflow capture and Halo KB SOP publishing."
requires-python = ">=3.10"
dependencies = [
  "fastapi>=0.111",
  "httpx>=0.27",
  "pydantic>=2.7",
  "requests>=2.31",
  "typer>=0.12",
  "uvicorn[standard]>=0.30",
  "watchdog>=4.0",
  "pillow>=10.0",
]

[project.optional-dependencies]
dev = [
  "pytest>=8.2",
  "ruff>=0.5",
]

[project.scripts]
sop-generator = "sop_generator.cli:main"

[tool.setuptools.packages.find]
where = ["src"]

[tool.ruff]
line-length = 100
target-version = "py310"
```

`src/sop_generator/__init__.py`:

```python
__version__ = "0.1.0"
```

`src/sop_generator/__main__.py`:

```python
from .cli import main


if __name__ == "__main__":
    main()
```

`src/sop_generator/cli.py`:

```python
import typer

app = typer.Typer(help="SOP Generator: browser workflow capture and Halo KB publishing.")


@app.command()
def serve(host: str = "127.0.0.1", port: int = 8765):
    """Run the local capture companion service."""
    typer.echo(f"Serving on http://{host}:{port}")


def main():
    app()
```

`sop_generator.py`:

```python
from sop_generator.cli import main


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run the CLI test**

Run: `python -m pytest tests/test_cli_import.py -q`

Expected: `1 passed`

- [ ] **Step 5: Commit**

```bash
git add pyproject.toml sop_generator.py src/sop_generator tests/test_cli_import.py
git commit -m "Add SOP generator package skeleton"
```

## Task 2: Local Paths and House Style File

**Files:**
- Create: `src/sop_generator/paths.py`
- Modify: `src/sop_generator/cli.py`
- Test: `tests/test_paths.py`

- [ ] **Step 1: Write path and style bootstrap tests**

```python
from sop_generator.paths import SopPaths


def test_default_paths_use_local_appdata(monkeypatch, tmp_path):
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    paths = SopPaths.default()
    assert paths.root == tmp_path / "MTG" / "SOPGenerator"
    assert paths.sessions == paths.root / "sessions"
    assert paths.house_style == paths.root / "house-style.md"


def test_ensure_default_style_writes_local_guidance(monkeypatch, tmp_path):
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    paths = SopPaths.default()
    written = paths.ensure_default_style()
    text = written.read_text(encoding="utf-8")
    assert "MTG technicians" in text
    assert "Do not include raw passwords" in text
```

- [ ] **Step 2: Run the tests and confirm failure**

Run: `python -m pytest tests/test_paths.py -q`

Expected: import failure for `sop_generator.paths`.

- [ ] **Step 3: Implement path helpers and the CLI command**

`src/sop_generator/paths.py`:

```python
import os
from dataclasses import dataclass
from pathlib import Path

DEFAULT_STYLE = """# MTG SOP House Style

Write for MTG technicians performing the work later.

- Start with a concise purpose and scope.
- Use numbered procedural steps.
- Preserve exact product and portal names.
- Call out decision points and verification evidence.
- Do not include raw passwords, MFA codes, API keys, session tokens, or recovery secrets.
- Replace sensitive customer-specific values with clear placeholders.
"""


@dataclass(frozen=True)
class SopPaths:
    root: Path
    sessions: Path
    house_style: Path

    @classmethod
    def default(cls) -> "SopPaths":
        base = Path(os.environ.get("LOCALAPPDATA") or Path.home() / ".local" / "share")
        root = base / "MTG" / "SOPGenerator"
        return cls(root=root, sessions=root / "sessions", house_style=root / "house-style.md")

    def ensure(self) -> "SopPaths":
        self.sessions.mkdir(parents=True, exist_ok=True)
        return self

    def ensure_default_style(self) -> Path:
        self.ensure()
        if not self.house_style.exists():
            self.house_style.write_text(DEFAULT_STYLE, encoding="utf-8")
        return self.house_style
```

Update `src/sop_generator/cli.py`:

```python
from pathlib import Path

import typer

from .paths import SopPaths

app = typer.Typer(help="SOP Generator: browser workflow capture and Halo KB publishing.")


@app.command("init-style")
def init_style():
    """Create the machine-local house style file if it does not exist."""
    path = SopPaths.default().ensure_default_style()
    typer.echo(str(path))
```

Keep the existing `serve` and `main` functions in the same file.

- [ ] **Step 4: Run tests and a CLI smoke check**

Run: `python -m pytest tests/test_paths.py tests/test_cli_import.py -q`

Expected: all tests pass.

Run: `python -m sop_generator init-style`

Expected: prints the local `house-style.md` path.

- [ ] **Step 5: Commit**

```bash
git add src/sop_generator/paths.py src/sop_generator/cli.py tests/test_paths.py
git commit -m "Add local SOP generator paths"
```

## Task 3: Data Models

**Files:**
- Create: `src/sop_generator/models.py`
- Test: `tests/test_models.py`

- [ ] **Step 1: Write model tests**

```python
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
```

- [ ] **Step 2: Run the tests and confirm failure**

Run: `python -m pytest tests/test_models.py -q`

Expected: import failure for `sop_generator.models`.

- [ ] **Step 3: Implement models**

```python
from datetime import datetime, timezone
from typing import Literal
from uuid import uuid4

from pydantic import BaseModel, Field

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
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


class CaptureEvent(BaseModel):
    type: EventType
    timestamp: datetime = Field(default_factory=utc_now)
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
```

- [ ] **Step 4: Run tests**

Run: `python -m pytest tests/test_models.py -q`

Expected: all tests pass.

- [ ] **Step 5: Commit**

```bash
git add src/sop_generator/models.py tests/test_models.py
git commit -m "Add SOP capture data models"
```

## Task 4: Session Storage

**Files:**
- Create: `src/sop_generator/storage.py`
- Test: `tests/test_storage.py`

- [ ] **Step 1: Write storage tests**

```python
import base64

from sop_generator.models import CaptureEvent
from sop_generator.paths import SopPaths
from sop_generator.storage import SessionStore


def make_store(tmp_path):
    return SessionStore(SopPaths(root=tmp_path, sessions=tmp_path / "sessions", house_style=tmp_path / "house-style.md"))


def test_create_session_writes_metadata(tmp_path):
    store = make_store(tmp_path)
    session = store.create_session("Customer onboarding")
    loaded = store.read_session(session.id)
    assert loaded.title == "Customer onboarding"


def test_append_and_read_events(tmp_path):
    store = make_store(tmp_path)
    session = store.create_session("Reset MFA")
    store.append_event(session.id, CaptureEvent(type="navigation", url="https://portal.test"))
    events = store.read_events(session.id)
    assert events[0].type == "navigation"


def test_write_screenshot_from_base64(tmp_path):
    store = make_store(tmp_path)
    session = store.create_session("Screenshot")
    encoded = base64.b64encode(b"png-bytes").decode("ascii")
    path = store.write_screenshot(session.id, encoded, "capture.png")
    assert path.name == "capture.png"
    assert path.read_bytes() == b"png-bytes"
```

- [ ] **Step 2: Run tests and confirm failure**

Run: `python -m pytest tests/test_storage.py -q`

Expected: import failure for `sop_generator.storage`.

- [ ] **Step 3: Implement storage**

Implement:
- `SessionStore.create_session(title: str) -> CaptureSession`
- `SessionStore.session_dir(session_id: str) -> Path`
- `SessionStore.write_session(session: CaptureSession) -> CaptureSession`
- `SessionStore.read_session(session_id: str) -> CaptureSession`
- `SessionStore.append_event(session_id: str, event: CaptureEvent) -> None`
- `SessionStore.read_events(session_id: str) -> list[CaptureEvent]`
- `SessionStore.write_screenshot(session_id: str, screenshot_base64: str, filename: str) -> Path`
- `SessionStore.write_draft(session_id: str, draft: DraftSop) -> Path`
- `SessionStore.read_draft(session_id: str) -> DraftSop`

Use `model_dump_json()` for JSON and one compact JSON object per line for events.

- [ ] **Step 4: Run tests**

Run: `python -m pytest tests/test_storage.py tests/test_models.py -q`

Expected: all tests pass.

- [ ] **Step 5: Commit**

```bash
git add src/sop_generator/storage.py tests/test_storage.py
git commit -m "Add local session storage"
```

## Task 5: Local Companion API

**Files:**
- Create: `src/sop_generator/service.py`
- Modify: `src/sop_generator/cli.py`
- Test: `tests/test_service.py`

- [ ] **Step 1: Write service tests**

```python
import base64

from fastapi.testclient import TestClient

from sop_generator.paths import SopPaths
from sop_generator.service import create_app


def test_health_endpoint(tmp_path):
    app = create_app(SopPaths(root=tmp_path, sessions=tmp_path / "sessions", house_style=tmp_path / "house-style.md"))
    assert TestClient(app).get("/health").json()["ok"] is True


def test_create_session_and_append_event(tmp_path):
    app = create_app(SopPaths(root=tmp_path, sessions=tmp_path / "sessions", house_style=tmp_path / "house-style.md"))
    client = TestClient(app)
    session = client.post("/api/sessions", json={"title": "Reset MFA"}).json()
    response = client.post(f"/api/sessions/{session['id']}/events", json={"type": "navigation", "url": "https://portal.test"})
    assert response.status_code == 200


def test_upload_screenshot(tmp_path):
    app = create_app(SopPaths(root=tmp_path, sessions=tmp_path / "sessions", house_style=tmp_path / "house-style.md"))
    client = TestClient(app)
    session = client.post("/api/sessions", json={"title": "Screenshot"}).json()
    payload = {"filename": "one.png", "screenshot_base64": base64.b64encode(b"png").decode("ascii")}
    response = client.post(f"/api/sessions/{session['id']}/screenshots", json=payload)
    assert response.status_code == 200
    assert response.json()["path"].endswith("one.png")
```

- [ ] **Step 2: Run tests and confirm failure**

Run: `python -m pytest tests/test_service.py -q`

Expected: import failure for `sop_generator.service`.

- [ ] **Step 3: Implement FastAPI app and real serve command**

`create_app(paths: SopPaths | None = None)` should create a `SessionStore` and expose:
- `GET /health`
- `POST /api/sessions` with `{"title": "..."}`
- `POST /api/sessions/{session_id}/events`
- `POST /api/sessions/{session_id}/screenshots` with `filename` and `screenshot_base64`

Update `serve` in `cli.py` to call:

```python
import uvicorn

from .service import create_app

uvicorn.run(create_app(), host=host, port=port)
```

- [ ] **Step 4: Run tests**

Run: `python -m pytest tests/test_service.py tests/test_storage.py -q`

Expected: all tests pass.

- [ ] **Step 5: Commit**

```bash
git add src/sop_generator/service.py src/sop_generator/cli.py tests/test_service.py
git commit -m "Add local companion capture API"
```

## Task 6: Step Grouping and Draft Generation

**Files:**
- Create: `src/sop_generator/steps.py`
- Create: `src/sop_generator/drafting.py`
- Modify: `src/sop_generator/service.py`
- Modify: `src/sop_generator/cli.py`
- Test: `tests/test_steps.py`
- Test: `tests/test_drafting.py`

- [ ] **Step 1: Write step grouping tests**

```python
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
```

- [ ] **Step 2: Write drafting tests**

```python
from sop_generator.drafting import draft_sop
from sop_generator.models import CaptureEvent


def test_draft_sop_uses_style_file(tmp_path):
    style = tmp_path / "house-style.md"
    style.write_text("Do not include raw passwords.", encoding="utf-8")
    draft = draft_sop("Reset MFA", [CaptureEvent(type="click", label="Reset MFA")], style)
    assert draft.title == "Reset MFA"
    assert draft.steps[0].action == "Select Reset MFA."
    assert any("secret" in warning.lower() for warning in draft.warnings)
```

- [ ] **Step 3: Run tests and confirm failure**

Run: `python -m pytest tests/test_steps.py tests/test_drafting.py -q`

Expected: import failures.

- [ ] **Step 4: Implement grouping and drafting**

`build_steps(events)` rules:
- Ignore `form_change`, `pause`, and `resume`.
- For `navigation`, create `Open {title or url}.`
- For `click`, create `Select {label or "the highlighted control"}.`
- For `submit`, create `Submit {label or "the form"}.`
- For `note`, use the note text as the action.
- Attach screenshot paths from the current event to the generated step evidence.

`draft_sop(title, events, style_file)` rules:
- Read the house style when present.
- Build a one-sentence summary: `Procedure captured from a browser workflow recording.`
- Add warning `Review screenshots and remove any visible secrets before publishing.` when the style mentions passwords, secrets, or tokens.

- [ ] **Step 5: Add draft endpoint and CLI command**

Expose `POST /api/sessions/{session_id}/draft`, which reads stored events, drafts the SOP, stores it as `draft.json`, and returns it.

Add CLI:

```python
@app.command()
def draft(session_id: str):
    """Draft an SOP from a captured session."""
```

The command should use `SessionStore(SopPaths.default())`, draft the SOP, write `draft.json`, and print the draft path.

- [ ] **Step 6: Run tests**

Run: `python -m pytest tests/test_steps.py tests/test_drafting.py tests/test_service.py -q`

Expected: all tests pass.

- [ ] **Step 7: Commit**

```bash
git add src/sop_generator/steps.py src/sop_generator/drafting.py src/sop_generator/service.py src/sop_generator/cli.py tests/test_steps.py tests/test_drafting.py tests/test_service.py
git commit -m "Add SOP draft generation"
```

## Task 7: Halo HTML Renderer

**Files:**
- Create: `src/sop_generator/render_halo.py`
- Modify: `src/sop_generator/cli.py`
- Test: `tests/test_render_halo.py`

- [ ] **Step 1: Write renderer tests**

```python
from sop_generator.models import DraftSop, SopStep
from sop_generator.render_halo import render_halo_html


def test_render_halo_html_escapes_text():
    draft = DraftSop(
        title="Reset <MFA>",
        summary="Use the portal.",
        warnings=["Remove secrets."],
        steps=[SopStep(order=1, action="Click <Reset>", evidence=["screenshots/one.png"])],
    )
    html = render_halo_html(draft)
    assert "&lt;MFA&gt;" in html
    assert "&lt;Reset&gt;" in html
    assert "screenshots/one.png" in html
```

- [ ] **Step 2: Run tests and confirm failure**

Run: `python -m pytest tests/test_render_halo.py -q`

Expected: import failure.

- [ ] **Step 3: Implement renderer and export command**

`render_halo_html(draft: DraftSop) -> str` should return escaped HTML with:
- `<h1>` title
- `<p>` summary
- warning list when warnings exist
- ordered list of steps
- image tags for evidence paths

Add CLI:

```python
@app.command()
def export(session_id: str, output: Path | None = None):
    """Render a reviewed draft as Halo-ready HTML."""
```

When `output` is omitted, write `halo-export.html` in the session directory and print the path.

- [ ] **Step 4: Run tests**

Run: `python -m pytest tests/test_render_halo.py -q`

Expected: all tests pass.

- [ ] **Step 5: Commit**

```bash
git add src/sop_generator/render_halo.py src/sop_generator/cli.py tests/test_render_halo.py
git commit -m "Add Halo HTML renderer"
```

## Task 8: Bifrost Publisher Client

**Files:**
- Create: `src/sop_generator/publish_bifrost.py`
- Modify: `src/sop_generator/cli.py`
- Test: `tests/test_publish_bifrost.py`

- [ ] **Step 1: Write publisher tests**

```python
import httpx

from sop_generator.publish_bifrost import BifrostPublisher


def test_publish_halo_posts_contract():
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/api/sop/halo/publish"
        assert request.headers["authorization"] == "Bearer token"
        return httpx.Response(200, json={"ok": True, "kb_article_id": "123", "url": "https://halo.test/kb/123"})

    client = httpx.Client(transport=httpx.MockTransport(handler))
    result = BifrostPublisher("https://bifrost.test", token="token", client=client).publish_halo(
        {"title": "Reset MFA", "html": "<h1>Reset MFA</h1>"}
    )
    assert result.ok is True
    assert result.kb_article_id == "123"
```

- [ ] **Step 2: Run tests and confirm failure**

Run: `python -m pytest tests/test_publish_bifrost.py -q`

Expected: import failure.

- [ ] **Step 3: Implement publisher and CLI command**

Implement `BifrostPublisher(base_url: str, token: str | None = None, client: httpx.Client | None = None)` with `publish_halo(payload: dict) -> PublishResult`.

Use endpoint `/api/sop/halo/publish`.

Add CLI:

```python
@app.command()
def publish(session_id: str, bifrost_url: str | None = None, token: str | None = None):
    """Publish Halo-ready HTML through Bifrost."""
```

Resolve `bifrost_url` from `--bifrost-url` or `BIFROST_URL`. Resolve token from `--token` or `BIFROST_TOKEN`. Read the session draft, render HTML, post `{"title": draft.title, "summary": draft.summary, "html": html}`.

- [ ] **Step 4: Run tests**

Run: `python -m pytest tests/test_publish_bifrost.py tests/test_render_halo.py -q`

Expected: all tests pass.

- [ ] **Step 5: Commit**

```bash
git add src/sop_generator/publish_bifrost.py src/sop_generator/cli.py tests/test_publish_bifrost.py
git commit -m "Add Bifrost Halo publisher client"
```

## Task 9: Browser Extension

**Files:**
- Create: `extension/browser/manifest.json`
- Create: `extension/browser/background.js`
- Create: `extension/browser/content.js`
- Create: `extension/browser/popup.html`
- Create: `extension/browser/popup.js`
- Create: `extension/browser/styles.css`
- Test: `tests/test_extension_files.py`

- [ ] **Step 1: Write extension file tests**

```python
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_manifest_declares_localhost_permission():
    manifest = json.loads((ROOT / "extension/browser/manifest.json").read_text(encoding="utf-8"))
    assert manifest["manifest_version"] == 3
    assert "http://127.0.0.1:8765/*" in manifest["host_permissions"]
    assert "storage" in manifest["permissions"]


def test_popup_has_visible_recording_controls():
    popup = (ROOT / "extension/browser/popup.html").read_text(encoding="utf-8")
    assert "Start" in popup
    assert "Pause" in popup
    assert "Stop" in popup
```

- [ ] **Step 2: Run tests and confirm failure**

Run: `python -m pytest tests/test_extension_files.py -q`

Expected: missing manifest file.

- [ ] **Step 3: Add Manifest V3 extension files**

Use:
- permissions: `activeTab`, `scripting`, `tabs`, `storage`
- host permissions: `http://127.0.0.1:8765/*`
- background service worker: `background.js`
- content script matches: `<all_urls>`
- popup: `popup.html`

`background.js` should keep `sessionId`, `recording`, and `paused` in `chrome.storage.local`, create sessions with `POST /api/sessions`, append navigation events on completed tab updates, and accept `capture-event` messages from `content.js`.

`content.js` should send events for:
- click with visible label text, current URL, document title
- submit with form label when available
- form_change with label and `value_hint: "changed"` without sending raw input values

`popup.js` should wire Start, Pause, Resume, and Stop buttons to background messages and keep the state visible.

- [ ] **Step 4: Run tests**

Run: `python -m pytest tests/test_extension_files.py -q`

Expected: all tests pass.

- [ ] **Step 5: Commit**

```bash
git add extension/browser tests/test_extension_files.py
git commit -m "Add browser capture extension"
```

## Task 10: Docs and Launcher

**Files:**
- Modify: `README.md`
- Modify: `QUICKSTART.md`
- Modify: `Start-SOPGenerator.ps1`
- Test: `tests/test_docs.py`

- [ ] **Step 1: Write docs smoke tests**

```python
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_readme_documents_local_capture_boundary():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "%LOCALAPPDATA%\\MTG\\SOPGenerator" in readme
    assert "Halo KB" in readme
    assert "Bifrost" in readme


def test_quickstart_mentions_browser_extension():
    quickstart = (ROOT / "QUICKSTART.md").read_text(encoding="utf-8")
    assert "extension/browser" in quickstart
    assert "python -m sop_generator serve" in quickstart
```

- [ ] **Step 2: Run tests and confirm failure**

Run: `python -m pytest tests/test_docs.py -q`

Expected: docs assertions fail against the old Greenshot workflow.

- [ ] **Step 3: Update docs**

README should explain:
- This is a local-first SOP recorder for human-led browser workflows.
- Raw capture stays machine-local in `%LOCALAPPDATA%\MTG\SOPGenerator`.
- The browser extension captures meaningful clicks, navigation, submits, notes, and screenshots.
- The Python companion drafts Halo KB-ready HTML.
- Publishing is through Bifrost, not direct Halo credentials in the extension.

QUICKSTART should include:

```powershell
python -m pip install -e .[dev]
python -m sop_generator init-style
python -m sop_generator serve --host 127.0.0.1 --port 8765
```

Then instruct the operator to load `extension/browser` as an unpacked extension in Edge or Chrome.

- [ ] **Step 4: Update launcher**

`Start-SOPGenerator.ps1` should run:

```powershell
param(
    [string]$HostName = "127.0.0.1",
    [int]$Port = 8765
)

python -m sop_generator init-style
python -m sop_generator serve --host $HostName --port $Port
```

- [ ] **Step 5: Run docs tests**

Run: `python -m pytest tests/test_docs.py -q`

Expected: all tests pass.

- [ ] **Step 6: Commit**

```bash
git add README.md QUICKSTART.md Start-SOPGenerator.ps1 tests/test_docs.py
git commit -m "Document browser-first SOP workflow"
```

## Task 11: End-to-End Local Smoke Test

**Files:**
- Create: `tests/test_end_to_end.py`

- [ ] **Step 1: Write the smoke test**

```python
import base64

from fastapi.testclient import TestClient

from sop_generator.paths import SopPaths
from sop_generator.render_halo import render_halo_html
from sop_generator.service import create_app


def test_capture_draft_and_render_flow(tmp_path):
    paths = SopPaths(root=tmp_path, sessions=tmp_path / "sessions", house_style=tmp_path / "house-style.md")
    paths.ensure_default_style()
    client = TestClient(create_app(paths))

    session = client.post("/api/sessions", json={"title": "Reset MFA"}).json()
    session_id = session["id"]
    client.post(f"/api/sessions/{session_id}/events", json={"type": "navigation", "title": "Admin Portal"})
    client.post(f"/api/sessions/{session_id}/events", json={"type": "click", "label": "Users"})
    client.post(
        f"/api/sessions/{session_id}/screenshots",
        json={"filename": "one.png", "screenshot_base64": base64.b64encode(b"png").decode("ascii")},
    )

    draft = client.post(f"/api/sessions/{session_id}/draft").json()
    html = render_halo_html(type("Draft", (), draft)()) if False else render_halo_html
    assert draft["title"] == "Reset MFA"
    assert draft["steps"][0]["action"] == "Open Admin Portal."
```

Replace the last two lines before committing with a direct `DraftSop.model_validate(draft)` call and assert the rendered HTML contains `Reset MFA`.

- [ ] **Step 2: Run the smoke test and confirm any integration gaps**

Run: `python -m pytest tests/test_end_to_end.py -q`

Expected before the replacement: failure caused by the intentionally invalid render call.

- [ ] **Step 3: Fix the smoke test and integration gaps**

Final test ending:

```python
from sop_generator.models import DraftSop

draft_model = DraftSop.model_validate(draft)
html = render_halo_html(draft_model)
assert "Reset MFA" in html
assert "Open Admin Portal." in html
```

Adjust service, storage, or drafting code only if this exposes a real mismatch between earlier tasks.

- [ ] **Step 4: Run the smoke test**

Run: `python -m pytest tests/test_end_to_end.py -q`

Expected: all tests pass.

- [ ] **Step 5: Commit**

```bash
git add tests/test_end_to_end.py src/sop_generator
git commit -m "Add SOP capture end-to-end smoke test"
```

## Task 12: Final Verification and PR

**Files:**
- Verify: entire repository

- [ ] **Step 1: Run the full test suite**

Run: `python -m pytest -q`

Expected: all tests pass.

- [ ] **Step 2: Run lint**

Run: `python -m ruff check src tests`

Expected: no lint failures.

- [ ] **Step 3: Run CLI smoke checks**

Run:

```powershell
python -m sop_generator --help
python -m sop_generator init-style
python -m sop_generator serve --help
python -m sop_generator publish --help
```

Expected: each command exits successfully. Do not leave a server process running after the smoke check.

- [ ] **Step 4: Review diff**

Run:

```bash
git status -sb
git diff --stat origin/master...HEAD
```

Expected: only SOP generator implementation, docs, extension, and tests changed.

- [ ] **Step 5: Push a review branch and open a PR**

Use branch `codex/browser-capture-halo-publishing`.

```bash
git checkout -b codex/browser-capture-halo-publishing
git push -u origin codex/browser-capture-halo-publishing
gh pr create --base master --head codex/browser-capture-halo-publishing --title "Add browser-first SOP capture workflow" --body "Adds the local companion API, browser extension, SOP drafting, Halo HTML export, and Bifrost publish client for the browser-first SOP Generator v1."
```

## Self-Review Checklist

- [ ] Spec coverage: human-led browser capture is covered by Tasks 5 and 9.
- [ ] Spec coverage: machine-local raw capture under `%LOCALAPPDATA%\MTG\SOPGenerator` is covered by Task 2 and Task 4.
- [ ] Spec coverage: mostly automatic draft with final review/export foundations is covered by Tasks 6 and 7.
- [ ] Spec coverage: Halo KB through Bifrost is covered by Task 8.
- [ ] Spec coverage: local prompt/style file is covered by Task 2 and consumed by Task 6.
- [ ] Deliberate deferral: rich local review UI is a follow-up; this plan creates the API, CLI, draft JSON, and Halo HTML foundations first.
- [ ] Deliberate deferral: Bifrost server-side Halo implementation is outside this repo; this repo implements and tests the client contract.
- [ ] Deliberate deferral: MSI and WinGet packaging should follow after the operator entry point stabilizes.
- [ ] Placeholder scan: verify the plan contains no banned placeholder markers and no unfinished function names before execution.
- [ ] Type consistency: keep `CaptureSession`, `CaptureEvent`, `SopStep`, `DraftSop`, and `PublishResult` signatures consistent across tests, API, and CLI.
