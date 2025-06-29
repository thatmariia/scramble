import typer
from scramble.cli.utils import require_session
from scramble.cli.state import set_current_session

round_app = typer.Typer(help="Manage rounds")


@round_app.command("start")
def start_round():
    """
    Start a new round and add it to the round history.
    """
    session = require_session()
    game_round = session.get_new_round()
    session.start_round(game_round)

    typer.secho("Started round:", fg=typer.colors.GREEN, bold=True)
    separator = "~" * 40
    typer.secho(separator, fg=typer.colors.BLUE)
    typer.secho(game_round, fg=typer.colors.BLUE)
    typer.secho(separator, fg=typer.colors.BLUE)

    set_current_session(session)


@round_app.command("undo")
def undo_round():
    """
    Undo the last round.
    """
    session = require_session()
    session.round_tracker.undo_last_round()
    typer.secho("Last round undone (if existed).", fg=typer.colors.YELLOW)
    set_current_session(session)


@round_app.command("undo-and-start")
def undo_and_start_new_round():
    """
    Undo the last round and start a new one.
    """
    session = require_session()
    session.round_tracker.undo_last_round()
    game_round = session.get_new_round()
    session.start_round(game_round)

    typer.secho("Last round undone and new round started:", fg=typer.colors.GREEN, bold=True)
    separator = "~" * 40
    typer.secho(separator, fg=typer.colors.BLUE)
    typer.secho(game_round, fg=typer.colors.BLUE)
    typer.secho(separator, fg=typer.colors.BLUE)

    set_current_session(session)


@round_app.command("history")
def show_round_history():
    """
    Show the history of all rounds.
    """
    session = require_session()
    typer.secho("Players history:", fg=typer.colors.GREEN, bold=True)
    typer.secho(session.round_tracker.history_manager, fg=typer.colors.BLUE)
    set_current_session(session)
