import typer
from scramble.services import handlers
from scramble.adapters.cli.state import get_session

round_app = typer.Typer(help="Manage rounds")


@round_app.command("start")
def start_round():
    """
    Start a new round and add it to the round history.
    """
    game_round = handlers.start_round(get_session())

    typer.secho("Started round:", fg=typer.colors.GREEN, bold=True)
    separator = "~" * 40
    typer.secho(separator, fg=typer.colors.BLUE)
    typer.secho(game_round, fg=typer.colors.BLUE)
    typer.secho(separator, fg=typer.colors.BLUE)


@round_app.command("undo")
def undo_round():
    """
    Undo the last round.
    """
    handlers.undo_round(get_session())
    typer.secho("Last round undone (if existed).", fg=typer.colors.YELLOW)

@round_app.command("count")
def count():
    """
    Get number of rounds in session.
    """
    session = get_session()
    typer.secho(f"{len(session.round_tracker)} rounds in session.", fg=typer.colors.YELLOW)

@round_app.command("get")
def get(index: int):
    """
    Get number of rounds in session.

    Parameters
    ----------
    index : str
        The round index (0-based).
    """
    session = get_session()
    round = session.round_tracker.get(index)
    if round is None:
        typer.secho(f"Round {index} not in session.", fg=typer.colors.BLUE)
        return

    typer.secho(f"{round}", fg=typer.colors.YELLOW)


@round_app.command("undo-and-start")
def undo_and_start_new_round():
    """
    Undo the last round and start a new one.
    """
    game_round = handlers.undo_and_start_new_round(get_session())

    typer.secho("Last round undone and new round started:", fg=typer.colors.GREEN, bold=True)
    separator = "~" * 40
    typer.secho(separator, fg=typer.colors.BLUE)
    typer.secho(game_round, fg=typer.colors.BLUE)
    typer.secho(separator, fg=typer.colors.BLUE)
