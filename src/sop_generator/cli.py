import typer

from sop_generator.paths import SopPaths

app = typer.Typer(help="SOP Generator: browser workflow capture and Halo KB publishing.")


@app.callback()
def callback() -> None:
    pass


@app.command()
def serve(host: str = "127.0.0.1", port: int = 8765) -> None:
    """Run the local capture companion service."""
    typer.echo(f"Serving on http://{host}:{port}")


@app.command("init-style")
def init_style() -> None:
    """Create the machine-local house style file if it does not exist."""
    path = SopPaths.default().ensure_default_style()
    typer.echo(str(path))


def main() -> None:
    app()
