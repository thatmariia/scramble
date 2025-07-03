from scramble.services import require_session, set_current_session
from scramble.core import Round
from scramble.app import AppSession


def start_round() -> Round:
    """
    Start a new round and add it to the round history.

    Returns
    -------
    Round
        The newly created round object.
    """
    session = require_session()
    game_round = session.get_new_round()
    session.start_round(game_round)
    set_current_session(session)
    return game_round


def undo_round():
    """
    Undo the last round.
    """
    session = require_session()
    session.round_tracker.undo_last_round()
    set_current_session(session)


def undo_and_start_new_round() -> Round:
    """
    Undo the last round and start a new one.

    Returns
    -------
    Round
        The newly created round object after undoing the last round.
    """
    session = require_session()
    session.round_tracker.undo_last_round()
    game_round = session.get_new_round()
    session.start_round(game_round)
    set_current_session(session)
    return game_round

