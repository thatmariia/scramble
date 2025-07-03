from fastapi import APIRouter
from scramble.services import handlers

router = APIRouter(tags=["Manage rounds"])


@router.post("/start", summary="Start a new round and add it to the round history.")
def start_round():
    """
    Start a new round and add it to the round history.
    """
    game_round = handlers.start_round()
    return {
        "message": "Started round",
        "round": str(game_round)
    }


@router.post("/undo", summary="Undo the last round.")
def undo_round():
    """
    Undo the last round.
    """
    handlers.undo_round()
    return {"message": "Last round undone (if existed)."}


@router.post("/undo-and-start", summary="Undo the last round and start a new one.")
def undo_and_start_new_round():
    """
    Undo the last round and start a new one.
    """
    game_round = handlers.undo_and_start_new_round()
    return {
        "message": "Last round undone and new round started",
        "round": str(game_round)
    }
