from fastapi import APIRouter, status, HTTPException, Query
from scramble.services import handlers
from scramble.adapters.api.schemas import RoundDTO
from scramble.adapters.api.cache import get_session

router = APIRouter(tags=["round"])


@router.post(
    "",
    operation_id="start_round",
    summary="Start round.",
    response_model=RoundDTO,
    status_code=status.HTTP_201_CREATED,
)
def start_round(session_name: str = Query(..., description="Name of the session to start the round in")):
    """
    Start a new round and add it to the round history.

    Parameters
    ----------
    session_name : str
        Name of the session in which to start the round.
    """
    session = get_session(session_name)
    game_round = handlers.start_round(session)
    return RoundDTO.from_domain(game_round)


@router.post(
    "/restart",
    operation_id="restart_round",
    summary="Restart round.",
    response_model=RoundDTO,
    status_code=status.HTTP_201_CREATED,
)
def undo_and_start_new_round(session_name: str = Query(..., description="Name of the session to restart the round in")):
    """
    Undo the last round and start a new one.

    Parameters
    ----------
    session_name : str
        Name of the session in which to undo the last round and start a new one.
    """
    try:
        session = get_session(session_name)
        game_round = handlers.undo_and_start_new_round(session)
        return RoundDTO.from_domain(game_round)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="No rounds to undo")


@router.delete(
    "",
    operation_id="undo_round",
    summary="Undo round.",
    status_code=status.HTTP_204_NO_CONTENT,
)
def undo_round(session_name: str = Query(..., description="Name of the session to undo the last round in")):
    """
    Undo the last round.

    Parameters
    ----------
    session_name : str
        Name of the session in which to undo the last round.
    """
    try:
        session = get_session(session_name)
        handlers.undo_round(session)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="No rounds to undo")


