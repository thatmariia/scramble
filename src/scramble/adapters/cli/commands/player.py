import typer
from scramble.core import Level
from scramble.services import handlers
from scramble.adapters.cli.state import get_session

player_app = typer.Typer(help="Manage players")


@player_app.command("get-max-assignment")
def get_max_assignment():
    """
    Get the maximum player assignment number in the current session.
    """
    max_assignment = handlers.get_max_player_assignment(get_session())
    typer.secho(f"Maximum player assignment: {max_assignment}", fg=typer.colors.GREEN)


@player_app.command("add")
def add_player(
        name: str,
        level: Level = typer.Option(..., help="Player's skill level"),
        assignment: str = typer.Option("", help="Player's assignment"),
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
    player = handlers.add_player(get_session(), name, level, assignment)
    typer.secho(f"Added player #{player.id}: {player.name} ({player.level})", fg=typer.colors.GREEN)


@player_app.command("remove")
def remove_player(player_id: str):
    """
    Remove a player by ID from the current session.

    Parameters
    ----------
    player_id : str
        The ID of the player to remove.
    """
    handlers.remove_player(get_session(), player_id)
    typer.secho(f"Removed player with ID {player_id}", fg=typer.colors.YELLOW)


@player_app.command("list")
def list_players():
    """
    List all players in the current session.
    """
    active_list, resting_list = handlers.list_players(get_session())

    typer.secho("Active Players:", fg=typer.colors.BLUE)
    if not active_list:
        typer.secho("No active players found.", fg=typer.colors.RED)
    else:
        for player in active_list:
            typer.echo(f" - {player}")

    typer.secho("Resting Players:", fg=typer.colors.CYAN)
    if not resting_list:
        typer.secho("No resting players found.", fg=typer.colors.RED)
    else:
        for player in resting_list:
            typer.echo(f" - {player}")


@player_app.command("toggle-rest")
def toggle_rest(player_id: str):
    """
    Toggle resting state of a player.

    Parameters
    ----------
    player_id : str
        The ID of the player whose resting state to toggle.
    """
    handlers.toggle_rest(get_session(), player_id)
    typer.secho(f"Toggled rest state of player #{player_id}", fg=typer.colors.MAGENTA)


@player_app.command("clear")
def clear_players():
    """
    Clear all players from the session.
    """
    handlers.clear_players(get_session())
    typer.secho("All players have been cleared", fg=typer.colors.YELLOW)
