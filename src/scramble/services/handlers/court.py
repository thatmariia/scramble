from scramble.core import Court
from scramble.services import require_session, set_current_session


def add_court(name: str) -> Court:
    """
    Add a new court to the current session.

    Parameters
    ----------
    name : str
        Name of the court.

    Returns
    -------
    Court
        The newly created court object.
    """
    session = require_session()
    court = Court(name=name)
    session.court_state.add(court)
    set_current_session(session)
    return court


def remove_court(court_id: str):
    """
    Remove a court by ID.

    Parameters
    ----------
    court_id : str
        ID of the court to remove.
    """
    session = require_session()
    session.court_state.remove(court_id)
    set_current_session(session)


def list_courts() -> list[Court]:
    """
    List all courts in the current session.

    Returns
    -------
    list[Court]
        A list of all courts in the current session.
    """
    session = require_session()
    courts = session.court_state.courts_list()
    return courts


def clear_courts():
    """
    Clear all courts from the current session.
    """
    session = require_session()
    session.court_state.clear()
    set_current_session(session)
