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
    team_of_player: dict
    court_of_player: dict
    # court_of_team: list
    players_same_team: dict
    players_same_court: dict
    players_same_court_diff_teams: dict
    nr_teams: int
    active_players: list[Player]
    courts: list[Court]
    history: HistoryManager
    settings: Settings
    _player_combos = None
    id_to_player: dict[str, Player] = None
    _teams_same_court_cache = None

    def __post_init__(self):
        self._player_combos = list(combinations(self.active_players, 2))
        self.id_to_player = {player.id: player for player in self.active_players}
        self.scale_weights()
        self._teams_same_court_cache = {}

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

    def players_in_same_court_diff_teams(self, mdl: CpModel):
        """
        Create a constraint that ensures players are on the same court if they are paired together
        but belong to different teams.
        This is done by creating a binary variable for each player pair and enforcing that they
        are on the same court if the variable is set.
        """
        if not self.players_same_court:
            self.players_on_same_court(mdl)

        if not self.players_same_team:
            self.players_in_same_team(mdl)

        players_same_court_diff_teams = {}
        for player1, player2 in self._player_combos:
            if player1.id == player2.id:
                continue
            same_court = self.players_same_court[(player1.id, player2.id)]
            same_team = self.players_same_team[(player1.id, player2.id)]

            valid_pair = define_and_var_imp(
                mdl,
                same_court,
                same_team.Not(),
                f"players_same_court_diff_teams_{player1.id}_{player2.id}"
            )

            players_same_court_diff_teams[(player1.id, player2.id)] = valid_pair
            players_same_court_diff_teams[(player2.id, player1.id)] = valid_pair

        self.players_same_court_diff_teams = players_same_court_diff_teams

    def players_on_same_court(self, mdl: CpModel):
        if not self.court_of_player:
            self.map_players_to_courts(mdl)

        players_same_court = {}
        for player1, player2 in self._player_combos:
            if player1.id == player2.id:
                continue
            same_court = mdl.new_bool_var(f"same_court_{player1.id}_{player2.id}")
            mdl.add(self.court_of_player[player1.id] == self.court_of_player[player2.id]).only_enforce_if(same_court)
            mdl.add(self.court_of_player[player1.id] != self.court_of_player[player2.id]).only_enforce_if(same_court.Not())
            players_same_court[(player1.id, player2.id)] = same_court
            players_same_court[(player2.id, player1.id)] = same_court

        self.players_same_court = players_same_court

    def players_in_same_team(self, mdl: CpModel):
        """
        Create a constraint that ensures players are in the same team if they are paired together.
        This is done by creating a binary variable for each player pair and enforcing that they
        belong to the same team if the variable is set.
        """
        if not self.team_of_player:
            self.map_players_to_teams(mdl)

        players_same_team = {}
        for player1, player2 in self._player_combos:
            if player1.id == player2.id:
                continue
            same_team = mdl.new_bool_var(f"same_team_{player1.id}_{player2.id}")
            mdl.add(self.team_of_player[player1.id] == self.team_of_player[player2.id]).only_enforce_if(same_team)
            mdl.add(self.team_of_player[player1.id] != self.team_of_player[player2.id]).only_enforce_if(same_team.Not())
            players_same_team[(player1.id, player2.id)] = same_team
            players_same_team[(player2.id, player1.id)] = same_team

        self.players_same_team = players_same_team

    def map_players_to_teams(self, mdl: CpModel):
        """
        Map players to teams, returning a dictionary where keys are player IDs and values are IntVars representing team indices.
        """
        team_of_player: dict[str, IntVar] = {}
        for player in self.active_players:
            tid = mdl.new_int_var(0, self.nr_teams - 1, f"team_of_{player.id}")
            team_of_player[player.id] = tid
            for team_id in range(self.nr_teams):
                mdl.add(tid == team_id).only_enforce_if(self.player_in_team[(player.id, team_id)])

        self.team_of_player = team_of_player

    def map_players_to_courts(self, mdl: CpModel):
        """
        Map players to courts, returning a dictionary where keys are player IDs and values are IntVars representing court indices.
        """
        court_id2idx = {court.id: i for i, court in enumerate(self.courts)}

        court_of_player: dict[str, IntVar] = {}
        for player in self.active_players:
            cvar = mdl.new_int_var(0, len(self.courts) - 1, f"court_of_{player.id}")
            court_of_player[player.id] = cvar
            # self.model.add_element(team_of_player[player.id], court_idx_of_team, cvar)
            for team_id in range(self.nr_teams):
                for court_id, court_idx in court_id2idx.items():
                    # player p is in team t AND team t is on court cid → p is on that court
                    cond = define_and_var(
                        mdl,
                        f"{player.id}_in_t{team_id}_on_c{court_id}",
                        [
                            self.player_in_team[(player.id, team_id)],
                            self.team_on_court[(team_id, court_id)]
                        ]
                    )
                    mdl.add(cvar == court_idx).only_enforce_if(cond)

        self.court_of_player = court_of_player

    def teams_on_same_court(self, mdl: CpModel, t1: int, t2: int):
        """
        Lazily creates and returns a BoolVar that is true iff
        teams t1 and t2 are assigned to the *same* court AND both teams are active.
        """
        key = (min(t1, t2), max(t1, t2))
        if key in self._teams_same_court_cache:
            return self._teams_same_court_cache[key]

        same_on_court = [
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
                define_or_var(mdl, f"t{t1}_t{t2}_same_court", same_on_court),
                self.team_active[t1],
                self.team_active[t2],
            ]
        )
        self._teams_same_court_cache[key] = var
        return var

    # def map_teams_to_courts(self, mdl: CpModel):
    #     """
    #     Map teams to courts, returning a list of IntVars where each index corresponds to a team.
    #     """
    #     court_id2idx = {court.id: i for i, court in enumerate(self.courts)}
    #
    #     court_idx_of_team: list[IntVar] = []
    #     for team_id in range(self.nr_teams):
    #         court_idx = mdl.new_int_var(0, len(self.courts) - 1, f"court_idx_t{team_id}")
    #         court_idx_of_team.append(court_idx)
    #         for court_id, idx in court_id2idx.items():
    #             mdl.add(court_idx == idx).only_enforce_if(self.team_on_court[(team_id, court_id)])
    #
    #     self.court_of_team = court_idx_of_team


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
