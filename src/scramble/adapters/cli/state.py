from scramble.app.app_session import AppSession

global_session = None


def set_session(session: AppSession):
    """
    Set the global session to the provided AppSession instance.
    This function is used to initialize the global session variable.

    Parameters
    ----------
    session : AppSession
        The AppSession instance to set as the global session.
    """

    global global_session
    global_session = session


def get_session() -> AppSession:
    """
    Get the current global session.
    This function retrieves the global session variable.
    If the session has not been set, it raises a ValueError.

    Returns
    -------
    AppSession
        The current global AppSession instance.

    Raises
    ------
    ValueError
        If the global session has not been set.
    """

    global global_session
    if global_session is None:
        raise ValueError("Session not set")

    return global_session
