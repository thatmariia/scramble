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
    response_model=int,
    status_code=status.HTTP_200_OK,
)
def undo_round(session_name: str = Query(..., description="Name of the session to undo the last round in")):
    """
    Undo the last round.

    Parameters
    ----------
    session_name : str
        Name of the session in which to undo the last round.

    Returns
    -------
    int
        The number of rounds remaining after undoing the last round.
    """
    try:
        session = get_session(session_name)
        handlers.undo_round(session)
        return len(session.round_tracker)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="No rounds to undo")

@router.get(
    "/round-count",
    operation_id="get_round_count",
    summary="Get the number of rounds in a session.",
    response_model=int,
    status_code=status.HTTP_200_OK
)
def get_round_count(session_name: str = Query(description="Session name")):
    """
    Get the number of rounds in a given session.

    Parameters
    ----------
    session_name : str
        The name of the session.

    Returns
    -------
    int
        The number of rounds in the session.
    """
    try:
        session = get_session(session_name)
        return len(session.round_tracker)
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

@router.get(
    "/round",
    operation_id="get_round_by_index",
    summary="Get a specific round from a session by index.",
    response_model=RoundDTO,  # Replace with actual DTO class
    status_code=status.HTTP_200_OK
)
def get_round_by_index(
    session_name: str = Query(description="Session name"),
    index: int = Query(description="Round index (0-based)")
):
    """
    Get a specific round from the session by index.

    Parameters
    ----------
    session_name : str
        The name of the session.
    index : int
        The index of the round to retrieve.

    Returns
    -------
    RoundDTO
        The round at the specified index.
    """
    try:
        session = get_session(session_name)
        round = session.round_tracker.get(index)
        if round is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Round does not exist"
            )
        return RoundDTO.from_domain(round)
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")