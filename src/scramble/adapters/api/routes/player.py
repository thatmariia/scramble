from fastapi import APIRouter, status, HTTPException, Query
from pydantic import BaseModel
from scramble.core import Level
from scramble.services import handlers
from scramble.adapters.api.schemas import PlayerDTO, PlayerListDTO
from scramble.adapters.api.cache import get_session

router = APIRouter(tags=["player"])


class PlayerCreate(BaseModel):
    name: str
    level: Level
    assignment: str = ""


@router.get(
    "/assignments",
    operation_id="get_max_player_assignment",
    summary="Get maximum player assignment.",
    response_model=int,
    status_code=status.HTTP_200_OK,
)
def get_max_player_assignment(
    session_name: str = Query(..., description="Name of the session to get the maximum assignment from")
):
    try:
        session = get_session(session_name)
        max_assignment = handlers.get_max_player_assignment(session)
        return max_assignment
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Assignments must be numeric values.")

@router.post(
    "",
    operation_id="add_player",
    summary="Add player.",
    response_model=PlayerDTO,
    status_code=status.HTTP_201_CREATED,
)
def add_player(
    payload: PlayerCreate,
    session_name: str = Query(..., description="Name of the session to add the player to")
):
    """
    Add a new player to the current session.

    Parameters
    ----------
    payload : PlayerCreate
        The player to add, containing the name and level of the player.
    session_name : str
        Name of the session to which the player will be added.
    """
    session = get_session(session_name)
    player = handlers.add_player(session, payload.name, payload.level, payload.assignment)
    return PlayerDTO.from_domain(player)


@router.get(
    "",
    operation_id="list_players",
    summary="List players.",
    response_model=PlayerListDTO,
    status_code=status.HTTP_200_OK
)
def list_players(session_name: str = Query(..., description="Name of the session to list players from")):
    """
    List all players in the current session.

    Parameters
    ----------
    session_name : str
        Name of the session from which to list players.
    """
    session = get_session(session_name)
    active_list, resting_list = handlers.list_players(session)
    return PlayerListDTO(
        active=[PlayerDTO.from_domain(player) for player in active_list],
        resting=[PlayerDTO.from_domain(player) for player in resting_list]
    )


@router.delete(
    "/{player_id}",
    operation_id="delete_player_by_id",
    summary="Delete player by ID.",
    status_code=status.HTTP_204_NO_CONTENT
)
def remove_player(
    player_id: str,
    session_name: str = Query(..., description="Name of the session to remove the player from")
):
    """
    Remove a player by ID from the current session.

    Parameters
    ----------
    player_id : str
        The ID of the player to remove.
    session_name : str
        Name of the session from which to remove the player.
    """
    try:
        session = get_session(session_name)
        handlers.remove_player(session, player_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Player not found")


@router.delete(
    "",
    operation_id="delete_all_players",
    summary="Delete all players.",
    status_code=status.HTTP_204_NO_CONTENT
)
def clear_players(session_name: str = Query(..., description="Name of the session to clear all players from")):
    """
    Clear all players from the session.

    Parameters
    ----------
    session_name : str
        Name of the session from which to clear all players.
    """
    session = get_session(session_name)
    handlers.clear_players(session)


@router.patch(
    "/{player-id}/toggle-rest",
    operation_id="toggle_rest_player",
    summary="Toggle player resting state.",
    response_model=PlayerListDTO,
    status_code=status.HTTP_200_OK
)
def toggle_rest(
    player_id: str,
    session_name: str = Query(..., description="Name of the session in which the player exists")
):
    """
    Toggle resting state of a player.

    Parameters
    ----------
    player_id : str
        The ID of the player whose resting state to toggle.
    session_name : str
        Name of the session in which the player exists.
    """
    try:
        session = get_session(session_name)
        active_list, resting_list = handlers.toggle_rest(session, player_id)
        return PlayerListDTO(
            active=[PlayerDTO.from_domain(player) for player in active_list],
            resting=[PlayerDTO.from_domain(player) for player in resting_list]
        )
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Player not found")

