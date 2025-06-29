import typer
from scramble.cli.commands import (
    player_app,
    court_app,
    round_app,
    session_app
)

app = typer.Typer(help="Scramble CLI")

# Register subcommands
app.add_typer(session_app, name="session")
app.add_typer(player_app, name="player")
app.add_typer(court_app, name="court")
app.add_typer(round_app, name="round")

if __name__ == "__main__":
    app()