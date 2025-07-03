from fastapi import APIRouter
from scramble.services import handlers

router = APIRouter(tags=["Manage courts"])


@router.post("/add", summary="Add a new court to the current session.")
def add_court(name: str):
    """
    Add a new court to the current session.

    Parameters
    ----------
    name : str
        Name of the court.
    """
    court = handlers.add_court(name)
    return {"message": f"Added court #{court.id}: {court.name}"}


@router.post("/remove", summary="Remove a court by ID.")
def remove_court(court_id: str):
    """
    Remove a court by ID.

    Parameters
    ----------
    court_id : str
        ID of the court to remove.
    """
    handlers.remove_court(court_id)
    return {"message": f"Removed court with ID {court_id}"}


@router.get("/list", summary="List all courts in the current session.")
def list_courts():
    """
    List all courts in the current session.
    """
    courts = handlers.list_courts()

    if not courts:
        return {"message": "No courts have been added yet."}

    courts_list = "\n".join(f" - {court}" for court in courts)

    return {"courts": courts_list}


@router.post("/clear", summary="Clear all courts from the current session.")
def clear_courts():
    """
    Clear all courts from the current session.
    """
    handlers.clear_courts()
    return {"message": "All courts have been cleared."}