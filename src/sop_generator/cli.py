import typer

app = typer.Typer(help="SOP Generator: browser workflow capture and Halo KB publishing.")


@app.callback()
def callback() -> None:
    pass


@app.command()
def serve(host: str = "127.0.0.1", port: int = 8765) -> None:
    typer.echo(f"Serving on http://{host}:{port}")


def main() -> None:
    app()
