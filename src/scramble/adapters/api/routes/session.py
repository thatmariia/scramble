from fastapi import APIRouter, status, HTTPException, Query
from pydantic import BaseModel
from pathlib import Path
from pydantic import Field
from scramble.services import handlers
from scramble.adapters.api.schemas import AppSessionDTO

router = APIRouter(tags=["session"])


class SessionCreate(BaseModel):
    name: str = Field()
    settings_path: str | None = Field(None)


@router.post(
    "",
    operation_id="new_session",
    summary="Start new session.",
    response_model=AppSessionDTO,
    status_code=status.HTTP_201_CREATED
)
def new_session(payload: SessionCreate):
    """
    Start a new session with the given name and settings.

    Parameters
    ----------
    payload : SessionCreate
        The session to create, containing the name and settings path.
        If no name is provided, a default name will be generated.
        If no settings path is provided, the default settings will be used.
    """
    settings_path = None
    if payload.settings_path:
        settings_path = Path(payload.settings_path)

    try:
        session = handlers.new_session(payload.name, settings_path)
        return AppSessionDTO.from_domain(session)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Session name '{payload.name}' already exists. Please choose a different name."
        )


@router.get(
    "/",
    operation_id="load_session",
    summary="Load session (by name ?name=… or latest).",
    response_model=AppSessionDTO,
    status_code=status.HTTP_200_OK
)
def load_session(name: str = Query(description="Session name")):
    """
    Load an existing session by name or the latest session if no name is provided.

    Parameters
    ----------
    name : str, optional
        The name of the session to load. If not provided, the latest session will be loaded.
    """
    try:
        session = handlers.load_session(name)
        return AppSessionDTO.from_domain(session)
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

@router.get(
    "/names",
    operation_id="list_session_names",
    summary="List all saved session names.",
    response_model=list[str],
    status_code=status.HTTP_200_OK
)
def list_session_names():
    """
    Retrieve the names of all saved sessions.

    Returns
    -------
    list of str
        A list of all session names.
    """
    return handlers.list_session_names()
