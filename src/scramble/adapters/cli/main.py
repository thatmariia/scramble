import click
import typer
import datetime
from click_shell import make_click_shell

from scramble.adapters.cli.commands import (
    player_app,
    court_app,
    round_app,
    session_app
)
from scramble.services.logging import configure_logging

app = typer.Typer(help="Scramble CLI")

app.add_typer(session_app, name="session", hidden=True)
app.add_typer(player_app, name="player", hidden=True)
app.add_typer(court_app, name="court", hidden=True)
app.add_typer(round_app, name="round", hidden=True)

@app.callback(invoke_without_command=True)
def base(ctx: typer.Context):
    if ctx.invoked_subcommand is None:
        typer.secho(" Session", fg=typer.colors.BLUE)
        typer.echo("   session new <session_name>")
        typer.echo("   session load <session_name>")
        typer.echo("   session default-settings <path>")
        typer.echo("")
        typer.secho(" Player", fg=typer.colors.BLUE)
        typer.echo("   player add <name> [level]")
        typer.echo("   player remove <player_id>")
        typer.echo("   player list")
        typer.echo("   player toggle-rest <player_id>")
        typer.echo("   player clear")
        typer.echo("")
        typer.secho(" Court", fg=typer.colors.BLUE)
        typer.echo("   court add <name>")
        typer.echo("   court remove <court_id>")
        typer.echo("   court list")
        typer.echo("   court clear")
        typer.echo("")
        typer.secho(" Round", fg=typer.colors.BLUE)
        typer.echo("   round start")
        typer.echo("   round undo")
        typer.echo("   round redo")
        typer.echo("   round clear")
        typer.echo("")
        typer.secho("Please enter a command or press enter to exit.", fg=typer.colors.BLUE)

        shell = make_click_shell(ctx, prompt='> ')

        def emptyline_handler():
            return True

        shell.emptyline = emptyline_handler
        shell.cmdloop()

log_file = f"logs/{datetime.datetime.now().strftime("logfile_%H_%M_%d_%m_%Y.log")}"
configure_logging(log_file, True, True)

if __name__ == "__main__":
    app()
