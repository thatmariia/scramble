from dataclasses import dataclass
from ortools.sat.python.cp_model import CpModel, IntVar
from itertools import combinations
from scramble.settings import Settings
from scramble.core import Player, HistoryManager, Court
from scramble.solver.utils import define_and_var, define_and_var_imp, define_or_var
# from scramble.solver.bounds import UpperBoundsComputer
from scramble.settings import Goal
from scramble.core import Level


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
    id_to_player: dict[str, Player] = None
    _teams_same_court_cache = None
    _players_same_court_diff_teams_cache = None
    _players_same_court_cache = None
    _players_same_team_cache = None
    _player_on_court_cache = None

    def __post_init__(self):
        self.id_to_player = {player.id: player for player in self.active_players}
        self.scale_weights()
        self._teams_same_court_cache = {}
        self._players_same_court_diff_teams_cache = {}
        self._players_same_court_cache = {}
        self._players_same_team_cache = {}
        self._player_on_court_cache = {}

    def scale_weights(self):
        def scale_weight(w_value, w_max, scale):
            if w_max == 0:
                return 0
            return int((w_value / w_max) * scale)

        ubc = UpperBoundsComputer(self)
        upper_bounds = ubc.compute_upper_bounds()
        # print upper bounds
        # print("\n\n")
        # print("Weight original")
        # for _, config in self.settings.goal_configs.items():
        #     print(config)
        # print()
        # print("Upper Bounds:")
        # for goal, ub in upper_bounds.items():
        #     print(f"{goal.value}: {ub}")
        # print()
        max_weight = 1000
        for goal, config in self.settings.goal_configs.items():
            if config.enabled:
                w_max = upper_bounds[goal]
                config.weight = scale_weight(config.weight, w_max, max_weight)
            else:
                config.weight = 0

        # print new weights
        # print("Scaled Weights:")
        # for _, config in self.settings.goal_configs.items():
        #     print(config)

    def teams_on_same_court(self, mdl: CpModel, t1: int, t2: int):
        """
        Lazily creates and returns a BoolVar that is true iff
        teams t1 and t2 are assigned to the *same* court AND both teams are active.
        """
        key = (min(t1, t2), max(t1, t2))
        if key in self._teams_same_court_cache:
            return self._teams_same_court_cache[key]

        same_court = [
            define_and_var(
                mdl,
                f"t{t1}_t{t2}_both_on_{c.id}",
                [self.team_on_court[(t1, c.id)],
                 self.team_on_court[(t2, c.id)]]
            )
            for c in self.courts
        ]
        var = define_and_var(
            mdl,
            f"t{t1}_t{t2}_same_court_and_active",
            [
                define_or_var(mdl, f"t{t1}_t{t2}_same_court", same_court),
                self.team_active[t1],
                self.team_active[t2],
            ]
        )
        self._teams_same_court_cache[key] = var
        return var

    def players_in_same_team(self, mdl: CpModel, p1_id: str, p2_id: str) -> IntVar:
        key = tuple(sorted((p1_id, p2_id)))
        if key in self._players_same_team_cache:
            return self._players_same_team_cache[key]

        both_in_same_team = [
            define_and_var(
                mdl,
                f"{p1_id}_{p2_id}_both_in_team_{t}",
                [self.player_in_team[(p1_id, t)], self.player_in_team[(p2_id, t)]]
            )
            for t in range(self.nr_teams)
        ]

        same_team = define_or_var(
            mdl,
            f"same_team_{p1_id}_{p2_id}",
            both_in_same_team
        )

        self._players_same_team_cache[key] = same_team
        return same_team

    def players_in_same_court_diff_team(self, mdl: CpModel, p1_id: str, p2_id: str) -> IntVar:
        key = tuple(sorted((p1_id, p2_id)))
        if key in self._players_same_court_diff_teams_cache:
            return self._players_same_court_diff_teams_cache[key]

        same_court = self._players_on_same_court(mdl, p1_id, p2_id)
        same_team = self.players_in_same_team(mdl, p1_id, p2_id)

        var = define_and_var_imp(
            mdl,
            same_court,
            same_team.Not(),
            f"players_same_court_diff_teams_{p1_id}_{p2_id}"
        )
        self._players_same_court_diff_teams_cache[key] = var
        return var

    def _players_on_same_court(self, mdl: CpModel, p1_id: str, p2_id: str) -> IntVar:
        key = tuple(sorted((p1_id, p2_id)))
        if key in self._players_same_court_cache:
            return self._players_same_court_cache[key]

        per_court = [
            define_and_var(
                mdl,
                f"{p1_id}_{p2_id}_both_on_{c.id}",
                [self._player_on_court(mdl, p1_id, c.id), self._player_on_court(mdl, p2_id, c.id)]
            )
            for c in self.courts
        ]

        var = define_or_var(mdl, f"{p1_id}_{p2_id}_same_court", per_court)
        self._players_same_court_cache[key] = var
        return var

    def _player_on_court(self, mdl: CpModel, player_id: str, court_id: str) -> IntVar:
        """
        Returns a BoolVar that is true iff the player is on the given court.
        """
        key = (player_id, court_id)
        if key in self._player_on_court_cache:
            return self._player_on_court_cache[key]

        per_team = [
            define_and_var(
                mdl,
                f"{player_id}_on_court_{court_id}_team_{t}",
                [self.player_in_team[(player_id, t)], self.team_on_court[(t, court_id)]]
            )
            for t in range(self.nr_teams)
        ]
        var = define_or_var(mdl,  f"{player_id}_on_court_{court_id}", per_team)
        self._player_on_court_cache[key] = var
        return var


class UpperBoundsComputer:
    """
    Computes upper bounds for various optimization goals based on the provided model variables.
    This class is used to determine the maximum possible values for each goal in the optimization process.
    """

    def __init__(self, mv: ModelVariables):
        self.mv = mv

    def compute_upper_bounds(self) -> dict[Goal, int]:
        """
        Computes upper bounds for all goals defined in the model variables.

        Return
        -------
        dict[Goal, int]
            A dictionary mapping each goal to its computed upper bound.
        """
        return {goal: self.compute_upper_bound(goal) for goal in self.mv.settings.goal_configs.keys()}

    def compute_upper_bound(self, goal: Goal) -> int:
        """
        Computes the upper bound for a specific goal.

        Parameters
        ----------
        goal : Goal
            The optimization goal for which to compute the upper bound.
        """
        match goal:
            case Goal.KEEP_IDEAL_TEAM_SIZE:
                return self._compute_ideal_team_size()
            case Goal.BALANCE_LVL:
                return self._compute_balance_level()
            case Goal.REDUCE_LVL_GAP:
                return self._compute_reduce_level_gap()
            case Goal.DIVERSIFY_PARTNERS:
                return self._compute_diversify_partners()
            case Goal.DIVERSIFY_OPPONENTS:
                return self._compute_diversify_opponents()
            case Goal.MAXIMIZE_COURTS_USAGE:
                return self._compute_maximize_courts_usage()
            case _:
                raise ValueError(f"Unknown goal: {goal}")

    def _compute_ideal_team_size(self) -> int:
        return self.mv.nr_teams * (self.mv.settings.max_team_size - self.mv.settings.min_team_size)

    def _compute_balance_level(self) -> int:
        return min(1000, self.mv.nr_teams * self.mv.nr_teams * self.mv.settings.max_team_size * Level.max_value())

    def _compute_reduce_level_gap(self) -> int:
        return self.mv.nr_teams * self.mv.settings.max_team_size * Level.max_value()

    def _compute_diversify_partners(self) -> int:
        return self.mv.history.get_all_partners_counts()

    def _compute_diversify_opponents(self) -> int:
        return self.mv.history.get_all_opponents_counts()

    def _compute_maximize_courts_usage(self) -> int:
        return len(self.mv.courts)
