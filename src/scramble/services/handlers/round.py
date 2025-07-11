from scramble.core import Round
from scramble.app import AppSession
from scramble.app.session_persistence import SessionPersistence


def start_round(session: AppSession) -> Round:
    """
    Start a new round and add it to the round history.

    Parameters
    ----------
    session : AppSession
        The current application session in which to start the round.

    Returns
    -------
    Round
        The newly created round object.
    """
    game_round = session.get_new_round()
    session.start_round(game_round)
    SessionPersistence.save(session)
    return game_round


def undo_round(session: AppSession):
    """
    Undo the last round.

    Parameters
    ----------
    session : AppSession
        The current application session from which to undo the last round.
    """
    session.round_tracker.undo_last_round()
    SessionPersistence.save(session)


def undo_and_start_new_round(session: AppSession) -> Round:
    """
    Undo the last round and start a new one.

    Parameters
    ----------
    session : AppSession
        The current application session in which to undo the last round and start a new one.

    Returns
    -------
    Round
        The newly created round object after undoing the last round.
    """
    session.round_tracker.undo_last_round()
    game_round = session.get_new_round()
    session.start_round(game_round)
    SessionPersistence.save(session)
    return game_round
