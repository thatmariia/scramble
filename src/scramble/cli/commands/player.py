import typer
from scramble.core import Player, Level
from scramble.cli.utils import require_session
from scramble.cli.state import set_current_session

player_app = typer.Typer(help="Manage players")


@player_app.command("add")
def add_player(
        name: str,
        level: Level = typer.Option(..., help="Player's skill level")
):
    """
    Add a new player to the current session.

    Parameters
    ----------
    name : str
        The name of the player to add.
    level : Level
        The skill level of the player. Must be one of the predefined levels.
    """
    session = require_session()

    player = Player(name=name, level=level)
    session.player_state.add(player)
    typer.secho(f"Added player #{player.id}: {player.name} ({player.level})", fg=typer.colors.GREEN)

    set_current_session(session)


@player_app.command("remove")
def remove_player(player_id: int):
    """
    Remove a player by ID from the current session.

    Parameters
    ----------
    player_id : int
        The ID of the player to remove.
    """
    session = require_session()
    session.player_state.remove(player_id)
    typer.secho(f"Removed player with ID {player_id}", fg=typer.colors.YELLOW)
    set_current_session(session)


@player_app.command("list")
def list_players():
    """
    List all players in the current session.
    """
    session = require_session()

    typer.secho("Active Players:", fg=typer.colors.BLUE)
    if not session.player_state.active_list():
        typer.secho("No active players found.", fg=typer.colors.RED)
    else:
        for player in session.player_state.active_list():
            typer.echo(f" - {player}")

    typer.secho("Resting Players:", fg=typer.colors.CYAN)
    if not session.player_state.resting_list():
        typer.secho("No resting players found.", fg=typer.colors.RED)
    else:
        for player in session.player_state.resting_list():
            typer.echo(f" - {player}")


@player_app.command("toggle-rest")
def toggle_rest(player_id: int):
    """
    Toggle resting state of a player.

    Parameters
    ----------
    player_id : int
        The ID of the player whose resting state to toggle.
    """
    session = require_session()
    session.player_state.toggle_rest(player_id)
    typer.secho(f"Toggled rest state of player #{player_id}", fg=typer.colors.MAGENTA)
    set_current_session(session)


@player_app.command("clear")
def clear_players():
    """
    Clear all players from the session.
    """
    session = require_session()
    session.player_state.clear()
    typer.secho("All players have been cleared", fg=typer.colors.YELLOW)
    set_current_session(session)
