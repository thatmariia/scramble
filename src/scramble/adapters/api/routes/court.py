from fastapi import APIRouter, status, HTTPException
from pydantic import BaseModel
from typing import List
from scramble.services import handlers
from scramble.adapters.api.schemas import CourtDTO
from scramble.adapters.api.cache import get_session

router = APIRouter(tags=["court"])

class CourtBase(BaseModel):
    session_name: str

class CourtCreate(CourtBase):
    name: str


@router.post(
    "",
    operation_id="add_court",
    summary="Add court.",
    response_model=CourtDTO,
    status_code=status.HTTP_201_CREATED,
)
def add_court(payload: CourtCreate):
    """
    Add a new court to the current session.

    Parameters
    ----------
    payload : CourtCreate
        The court to add, containing the name of the court and the session name.
    """
    session = get_session(payload.session_name)
    court = handlers.add_court(session, payload.name)
    return CourtDTO.from_domain(court)


@router.get(
    "",
    operation_id="list_courts",
    summary="List courts.",
    response_model=List[CourtDTO],
    status_code=status.HTTP_200_OK
)
def list_courts(payload: CourtBase):
    """
    List all courts in the current session.

    Parameters
    ----------
    payload : CourtBase
        The session to list courts from, containing the session name.
    """
    session = get_session(payload.session_name)
    courts = handlers.list_courts(session)
    return [CourtDTO.from_domain(court) for court in courts]


@router.delete(
    "/{court_id}",
    operation_id="delete_court_by_id",
    summary="Delete court by ID.",
    status_code=status.HTTP_204_NO_CONTENT
)
def remove_court(session_name: str, court_id: str):
    """
    Remove a court by ID.

    Parameters
    ----------
    court_id : str
        ID of the court to remove.
    session_name : str
        Name of the session from which to remove the court.
    """
    try:
        session = get_session(session_name)
        handlers.remove_court(session, court_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Court not found")


@router.delete(
    "",
    operation_id="delete_all_courts",
    summary="Delete all courts.",
    status_code=status.HTTP_204_NO_CONTENT
)
def clear_courts(session_name):
    """
    Clear all courts from the current session.

    Parameters
    ----------
    session_name : str
        Name of the session from which to clear all courts.
    """
    session = get_session(session_name)
    handlers.clear_courts(session)
