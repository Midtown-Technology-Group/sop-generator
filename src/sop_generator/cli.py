import os
from pathlib import Path

import httpx
import typer
import uvicorn

from sop_generator.drafting import draft_sop
from sop_generator.paths import SopPaths
from sop_generator.publish_bifrost import BifrostPublisher
from sop_generator.render_halo import render_halo_html
from sop_generator.service import create_app
from sop_generator.storage import SessionStore

app = typer.Typer(help="SOP Generator: browser workflow capture and Halo KB publishing.")


@app.callback()
def callback() -> None:
    pass


@app.command()
def serve(host: str = "127.0.0.1", port: int = 8765) -> None:
    """Run the local capture companion service."""
    uvicorn.run(create_app(), host=host, port=port)


@app.command("init-style")
def init_style() -> None:
    """Create the machine-local house style file if it does not exist."""
    path = SopPaths.default().ensure_default_style()
    typer.echo(str(path))


@app.command()
def draft(session_id: str) -> None:
    """Draft an SOP from captured events for a session."""
    store = SessionStore(SopPaths.default())
    try:
        session = store.read_session(session_id)
    except FileNotFoundError:
        raise typer.BadParameter(f"Session not found: {session_id}") from None
    except ValueError:
        raise typer.BadParameter(f"Invalid session id: {session_id}") from None
    draft = draft_sop(session.title, store.read_events(session_id), store.paths.house_style)
    path = store.write_draft(session_id, draft)
    typer.echo(str(path))


def _abort(message: str) -> None:
    typer.echo(message, err=True)
    raise typer.Exit(1)


@app.command()
def export(session_id: str, output: Path | None = None) -> None:
    """Render a reviewed draft as Halo-ready HTML."""
    store = SessionStore(SopPaths.default())
    try:
        store.read_session(session_id)
    except FileNotFoundError:
        _abort(f"Session not found: {session_id}")
    except ValueError:
        _abort(f"Invalid session id: {session_id}")

    try:
        reviewed_draft = store.read_draft(session_id)
    except FileNotFoundError:
        _abort(f"Draft not found for session: {session_id}")
    except ValueError:
        _abort(f"Invalid draft for session: {session_id}")

    output_path = output or store.session_dir(session_id) / "halo-export.html"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(render_halo_html(reviewed_draft), encoding="utf-8")
    typer.echo(str(output_path))


@app.command()
def publish(session_id: str, bifrost_url: str | None = None, token: str | None = None) -> None:
    """Publish Halo-ready HTML through Bifrost."""
    resolved_url = bifrost_url or os.environ.get("BIFROST_URL")
    resolved_token = token or os.environ.get("BIFROST_TOKEN")
    if not resolved_url:
        _abort("Bifrost URL is required. Use --bifrost-url or set BIFROST_URL.")

    store = SessionStore(SopPaths.default())
    try:
        store.read_session(session_id)
    except FileNotFoundError:
        _abort(f"Session not found: {session_id}")
    except ValueError:
        _abort(f"Invalid session id: {session_id}")

    try:
        reviewed_draft = store.read_draft(session_id)
    except FileNotFoundError:
        _abort(f"Draft not found for session: {session_id}")
    except ValueError:
        _abort(f"Invalid draft for session: {session_id}")

    publisher = BifrostPublisher(resolved_url, token=resolved_token, client=httpx.Client())
    payload = {
        "title": reviewed_draft.title,
        "summary": reviewed_draft.summary,
        "html": render_halo_html(reviewed_draft),
    }
    try:
        result = publisher.publish_halo(payload)
    except httpx.HTTPError as exc:
        _abort(f"Publish failed: {exc}")

    if result.url:
        typer.echo(f"Published Halo KB article: {result.url}")
    elif result.kb_article_id:
        typer.echo(f"Published Halo KB article {result.kb_article_id}")
    else:
        typer.echo(result.message or "Published Halo KB article.")


def main() -> None:
    app()
