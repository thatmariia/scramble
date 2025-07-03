from fastapi import APIRouter
from scramble.services import handlers

router = APIRouter(tags=["Manage application sessions"])


@router.post("/new", summary="Start a new session with the given name and settings.")
def new_session(name: str = None, settings_path: str = None):
    """
    Start a new session with the given name and settings.

    Parameters
    ----------
    name : str, optional
        The name of the new session. If not provided, a default name will be generated.
    settings_path : str, optional
        Path to a JSON file containing settings. If not provided, default settings will be used.
    """
    session = handlers.new_session(name, settings_path)
    return {"message": f"Started new session: {session.session_name}"}


@router.post("/load", summary="Load an existing session by name or the latest session if no name is provided.")
def load_session(name: str = None):
    """
    Load an existing session by name or the latest session if no name is provided.

    Parameters
    ----------
    name : str, optional
        The name of the session to load. If not provided, the latest session will be loaded.
    """
    session = handlers.load_session(name)
    if session is None:
        return {"message": "No session found."}
    return {"message": f"Loaded session: {session.session_name}"}


@router.post("/save", summary="Save the current session to disk.")
def save_session():
    """
    Save the current session to disk.
    """
    session = handlers.save_session()
    return {"message": f"Session '{session.session_name}' saved successfully."}