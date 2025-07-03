from fastapi import APIRouter
from scramble.core import Level
from scramble.services import handlers

router = APIRouter(tags=["Manage players"])


@router.post("/add", summary="Add a new player to the current session.")
def add_player(name: str, level: Level):
    """
    Add a new player to the current session.

    Parameters
    ----------
    name : str
        The name of the player to add.
    level : Level
        The skill level of the player. Must be one of the predefined levels.
    """
    player = handlers.add_player(name, level)
    return {"message": f"Added player #{player.id}: {player.name} ({player.level})"}


@router.post("/remove", summary="Remove a player by ID from the current session.")
def remove_player(player_id: str):
    """
    Remove a player by ID from the current session.

    Parameters
    ----------
    player_id : str
        The ID of the player to remove.
    """
    handlers.remove_player(player_id)
    return {"message": f"Removed player with ID {player_id}"}


@router.get("/list", summary="List all players in the current session.")
def list_players():
    """
    List all players in the current session.
    """
    active_list, resting_list = handlers.list_players()

    active_players = "Active Players:\n"
    active_players += "\n".join(f" - {player}" for player in active_list) \
        if active_list else "No active players found."
    resting_players = "Resting Players:\n"
    resting_players += "\n".join(f" - {player}" for player in resting_list) \
        if resting_list else "No resting players found."
    return {
        "active_players": active_players,
        "resting_players": resting_players
    }


@router.post("/toggle-rest", summary="Toggle resting state of a player.")
def toggle_rest(player_id: str):
    """
    Toggle resting state of a player.

    Parameters
    ----------
    player_id : str
        The ID of the player whose resting state to toggle.
    """
    handlers.toggle_rest(player_id)
    return {"message": f"Toggled rest state for player with ID {player_id}"}


@router.post("/clear", summary="Clear all players from the session.")
def clear_players():
    """
    Clear all players from the session.
    """
    handlers.clear_players()
    return {"message": "All players have been cleared."}
