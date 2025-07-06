from scramble.core import Player, Level
from scramble.app import AppSession
from scramble.app.session_persistence import SessionPersistence


def add_player(session: AppSession, name: str, level: Level) -> Player:
    """
    Add a new player to the current session.

    Parameters
    ----------
    session : AppSession
        The current application session.
    name : str
        The name of the player to add.
    level : Level
        The skill level of the player. Must be one of the predefined levels.

    Returns
    -------
    Player
        The newly created player object.
    """
    player = Player(name=name, level=level)
    session.player_state.add(player)
    SessionPersistence.save(session)
    return player


def remove_player(session: AppSession, player_id: str):
    """
    Remove a player by ID from the current session.

    Parameters
    ----------
    session : AppSession
        The current application session.
    player_id : str
        The ID of the player to remove.
    """
    session.player_state.remove(player_id)
    SessionPersistence.save(session)


def list_players(session: AppSession) -> tuple[list[Player], list[Player]]:
    """
    List all players in the current session.
    """
    active_list = session.player_state.active_list()
    resting_list = session.player_state.resting_list()
    return active_list, resting_list


def toggle_rest(session: AppSession, player_id: str) -> tuple[list[Player], list[Player]]:
    """
    Toggle resting state of a player.

    Parameters
    ----------
    session : AppSession
        The current application session.
    player_id : str
        The ID of the player whose resting state to toggle.
    """
    player = session.player_state.toggle_rest(player_id)
    SessionPersistence.save(session)
    return session.player_state.active_list(), session.player_state.resting_list()


def clear_players(session: AppSession):
    """
    Clear all players from the session.

    Parameters
    ----------
    session : AppSession
        The current application session from which to clear all players.
    """
    session.player_state.clear()
    SessionPersistence.save(session)
