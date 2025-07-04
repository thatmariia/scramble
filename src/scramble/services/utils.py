import datetime
from scramble.services.state import get_current_session
from scramble.services.logging import configure_logging
from scramble.app import AppSession
from scramble.app.session_name_manager import SessionNameManager


def require_session() -> AppSession | None:
    """
    Ensure that a session is currently active and configure logging for it.

    Returns
    -------
    AppSession | None
        The current active session. If no session is active, returns None.
    """
    session = get_current_session()
    if not session:
        # TODO: handle this case more gracefully, e.g., by raising an exception
        return None

    log_dir = SessionNameManager.SESSIONS_DIR / session.session_name
    log_file = log_dir / datetime.datetime.now().strftime("logfile_%H_%M_%d_%m_%Y.log")
    configure_logging(log_file, session.settings.log_verbose, not session.settings.log_enabled)
    return session
