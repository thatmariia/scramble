from fastapi import APIRouter, status, HTTPException
from scramble.services import handlers
from scramble.adapters.api.schemas import RoundDTO

router = APIRouter(tags=["Manage rounds"])


@router.post(
    "",
    summary="Start a new round and add it to the round history.",
    response_model=RoundDTO,
    status_code=status.HTTP_201_CREATED,
)
def start_round():
    """
    Start a new round and add it to the round history.
    """
    game_round = handlers.start_round()
    return RoundDTO.from_domain(game_round)


@router.post(
    "/restart",
    summary="Undo the last round and start a new one.",
    response_model=RoundDTO,
    status_code=status.HTTP_201_CREATED,
)
def undo_and_start_new_round():
    """
    Undo the last round and start a new one.
    """
    try:
        game_round = handlers.undo_and_start_new_round()
        return RoundDTO.from_domain(game_round)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="No rounds to undo")


@router.delete(
    "",
    summary="Undo the last round.",
    status_code=status.HTTP_204_NO_CONTENT,
)
def undo_round():
    """
    Undo the last round.
    """
    try:
        handlers.undo_round()
    except ValueError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="No rounds to undo")


