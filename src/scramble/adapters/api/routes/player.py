from fastapi import APIRouter, status, HTTPException
from pydantic import BaseModel
from scramble.core import Level
from scramble.services import handlers
from scramble.adapters.api.schemas import PlayerDTO, PlayerListDTO
from scramble.adapters.api.cache import get_session

router = APIRouter(tags=["player"])

class PlayerBase(BaseModel):
    session_name: str

class PlayerCreate(PlayerBase):
    name: str
    level: Level


@router.post(
    "",
    operation_id="add_player",
    summary="Add player.",
    response_model=PlayerDTO,
    status_code=status.HTTP_201_CREATED,
)
def add_player(payload: PlayerCreate):
    """
    Add a new player to the current session.

    Parameters
    ----------
    payload : PlayerCreate
        The player to add, containing the name and level of the player and the session name.
    """
    session = get_session(payload.session_name)
    player = handlers.add_player(session, payload.name, payload.level)
    return PlayerDTO.from_domain(player)


@router.get(
    "",
    operation_id="list_players",
    summary="List players.",
    response_model=PlayerListDTO,
    status_code=status.HTTP_200_OK
)
def list_players(payload: PlayerBase):
    """
    List all players in the current session.

    Parameters
    ----------
    payload : PlayerBase
        The session to list players from, containing the session name.
    """
    session = get_session(payload.session_name)
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
def remove_player(session_name: str, player_id: str):
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
def clear_players(session_name: str):
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
def toggle_rest(session_name: str, player_id: str):
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

