from scramble.core import Court
from scramble.app import AppSession
from scramble.app.session_persistence import SessionPersistence


def add_court(session: AppSession, name: str) -> Court:
    """
    Add a new court to the current session.

    Parameters
    ----------
    session : AppSession
        The current application session.
    name : str
        Name of the court.

    Returns
    -------
    Court
        The newly created court object.
    """
    court = Court(name=name)
    session.court_state.add(court)
    SessionPersistence.save(session)
    return court


def remove_court(session: AppSession, court_id: str):
    """
    Remove a court by ID.

    Parameters
    ----------
    session : AppSession
        The current application session.
    court_id : str
        ID of the court to remove.
    """
    session.court_state.remove(court_id)
    SessionPersistence.save(session)


def list_courts(session: AppSession) -> list[Court]:
    """
    List all courts in the current session.

    Parameters
    ----------
    session : AppSession
        The current application session.

    Returns
    -------
    list[Court]
        A list of all courts in the current session.
    """
    courts = session.court_state.courts_list()
    return courts


def clear_courts(session: AppSession):
    """
    Clear all courts from the current session.
    """
    session.court_state.clear()
    SessionPersistence.save(session)
