from dataclasses import dataclass
from scramble.settings import Settings
from scramble.core import Player, HistoryManager, Court


@dataclass
class ModelVariables:
    """
    A collection of decision variables used in the CP model and other variables.
    This class holds all the necessary variables for the objective function.
    """
    player_in_team: dict
    team_on_court: dict
    team_active: dict
    court_active: dict
    nr_teams: int
    active_players: list[Player]
    courts: list[Court]
    history: HistoryManager
    settings: Settings