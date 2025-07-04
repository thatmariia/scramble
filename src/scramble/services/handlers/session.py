import json
from pathlib import Path
from scramble.app.app_session import AppSession
from scramble.app.session_persistence import SessionPersistence, SessionNameManager
from scramble.settings import Settings
from scramble.services import require_session, set_current_session


def new_session(name: str | None, settings_path: Path | None) -> AppSession:
    """
    Start a new session with the given name and settings.

    Parameters
    ----------
    name : str | None
        The name of the new session. If None, a default name will be generated.
    settings_path : Path | None
        Path to a JSON file containing settings. If None, default settings will be used.

    Returns
    -------
    AppSession
        The newly created session object.
    """
    if settings_path and settings_path.is_file():
        with open(settings_path, "r") as f:
            settings = Settings.from_dict(json.load(f))
    else:
        settings = Settings()

    session_name = name or SessionNameManager.generate_name()
    session = AppSession(settings=settings, session_name=session_name)
    set_current_session(session)

    SessionPersistence.save(session)

    return session


def load_session(name: str | None = None) -> AppSession | None:
    """
    Load an existing session by name or the latest session if no name is provided.

    Parameters
    ----------
    name : str, optional
        The name of the session to load. If None, the latest session will be loaded.

    Returns
    -------
    AppSession | None
        The loaded session object, or None if no session is found.
    """
    session = SessionPersistence.load(name)
    set_current_session(session)
    return session
