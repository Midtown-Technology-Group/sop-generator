import typer
import uvicorn

from sop_generator.drafting import draft_sop
from sop_generator.paths import SopPaths
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


def main() -> None:
    app()
