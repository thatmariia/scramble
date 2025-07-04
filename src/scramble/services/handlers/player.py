from scramble.core import Player, Level
from scramble.services import require_session, set_current_session


def add_player(name: str, level: Level) -> Player:
    """
    Add a new player to the current session.

    Parameters
    ----------
    name : str
        The name of the player to add.
    level : Level
        The skill level of the player. Must be one of the predefined levels.

    Returns
    -------
    Player
        The newly created player object.
    """
    session = require_session()
    player = Player(name=name, level=level)
    session.player_state.add(player)
    set_current_session(session)
    return player


def remove_player(player_id: str):
    """
    Remove a player by ID from the current session.

    Parameters
    ----------
    player_id : str
        The ID of the player to remove.
    """
    session = require_session()
    session.player_state.remove(player_id)
    set_current_session(session)


def list_players() -> tuple[list[Player], list[Player]]:
    """
    List all players in the current session.
    """
    session = require_session()
    active_list = session.player_state.active_list()
    resting_list = session.player_state.resting_list()
    return active_list, resting_list


def toggle_rest(player_id: str) -> Player:
    """
    Toggle resting state of a player.

    Parameters
    ----------
    player_id : str
        The ID of the player whose resting state to toggle.
    """
    session = require_session()
    player = session.player_state.toggle_rest(player_id)
    set_current_session(session)
    return player


def clear_players():
    """
    Clear all players from the session.
    """
    session = require_session()
    session.player_state.clear()
    set_current_session(session)
