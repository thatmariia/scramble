from fastapi import APIRouter, status, HTTPException
from pydantic import BaseModel
from typing import List
from scramble.services import handlers
from scramble.adapters.api.schemas import CourtDTO

router = APIRouter(tags=["Manage courts"])


class CourtCreate(BaseModel):
    name: str


@router.post(
    "",
    summary="Add a new court to the current session.",
    response_model=CourtDTO,
    status_code=status.HTTP_201_CREATED,
)
def add_court(payload: CourtCreate):
    """
    Add a new court to the current session.

    Parameters
    ----------
    payload : CourtCreate
        The court to add, containing the name of the court.
    """
    court = handlers.add_court(payload.name)
    return CourtDTO.from_domain(court)


@router.get(
    "",
    summary="List all courts in the current session.",
    response_model=List[CourtDTO],
    status_code=status.HTTP_200_OK
)
def list_courts():
    """
    List all courts in the current session.
    """
    courts = handlers.list_courts()
    return [CourtDTO.from_domain(court) for court in courts]


@router.delete(
    "/{court_id}",
    summary="Remove a court by ID.",
    status_code=status.HTTP_204_NO_CONTENT
)
def remove_court(court_id: str):
    """
    Remove a court by ID.

    Parameters
    ----------
    court_id : str
        ID of the court to remove.
    """
    try:
        handlers.remove_court(court_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Court not found")


@router.delete(
    "",
    summary="Clear all courts from the current session.",
    status_code=status.HTTP_204_NO_CONTENT
)
def clear_courts():
    """
    Clear all courts from the current session.
    """
    handlers.clear_courts()
