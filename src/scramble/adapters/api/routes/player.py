from fastapi import APIRouter, status, HTTPException
from pydantic import BaseModel
from scramble.core import Level
from scramble.services import handlers
from scramble.adapters.api.schemas import PlayerDTO, PlayerListDTO

router = APIRouter(tags=["Manage players"])


class PlayerCreate(BaseModel):
    name: str
    level: Level


@router.post(
    "",
    summary="Add a new player to the current session.",
    response_model=PlayerDTO,
    status_code=status.HTTP_201_CREATED,
)
def add_player(payload: PlayerCreate):
    """
    Add a new player to the current session.

    Parameters
    ----------
    payload : PlayerCreate
        The player to add, containing the name and level of the player.
    """
    player = handlers.add_player(payload.name, payload.level)
    return PlayerDTO.from_domain(player)


@router.get(
    "",
    summary="List all players in the current session.",
    response_model=PlayerListDTO,
    status_code=status.HTTP_200_OK
)
def list_players():
    """
    List all players in the current session.
    """
    active_list, resting_list = handlers.list_players()
    return PlayerListDTO(
        active=[PlayerDTO.from_domain(player) for player in active_list],
        resting=[PlayerDTO.from_domain(player) for player in resting_list]
    )


@router.delete(
    "/{player_id}",
    summary="Remove a player by ID from the current session.",
    status_code=status.HTTP_204_NO_CONTENT
)
def remove_player(player_id: str):
    """
    Remove a player by ID from the current session.

    Parameters
    ----------
    player_id : str
        The ID of the player to remove.
    """
    try:
        handlers.remove_player(player_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Player not found")


@router.delete(
    "",
    summary="Clear all players from the session.",
    status_code=status.HTTP_204_NO_CONTENT
)
def clear_players():
    """
    Clear all players from the session.
    """
    handlers.clear_players()


@router.patch(
    "/{player-id}/toggle-rest",
    summary="Toggle resting state of a player.",
    response_model=PlayerDTO,
    status_code=status.HTTP_200_OK
)
def toggle_rest(player_id: str):
    """
    Toggle resting state of a player.

    Parameters
    ----------
    player_id : str
        The ID of the player whose resting state to toggle.
    """
    try:
        player = handlers.toggle_rest(player_id)
        return PlayerDTO.from_domain(player)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Player not found")

