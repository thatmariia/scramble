# external imports
from ortools.sat.python import cp_model as cp

import heapq
import math
from itertools import combinations
from scramble.core import Player, HistoryManager, Match, Court, Round
from scramble.settings import Settings
from scramble.solver.utils import are_disjoint
from scramble.solver.scoring import score_match, score_team


class ScrambleSolver:
    """
    Responsible for solving the scramble scheduling problem using OR-Tools CP-SAT solver,
    aka Constraint Programming Solver.
    This class defines the optimization model, adds constraints, and sets the objective function
    based on scoring functions.

    Attributes
    ----------
    active_players : list[Player]
        List of players to be assigned to teams and matches.
    _player_lookup : dict[str, Player]
        Dictionary mapping player IDs to Player objects for quick access.
    history : HistoryManager
        The history manager containing player histories.
    settings : Settings
        The settings for the scramble solver.
    model : cp.CpModel
        The CP-SAT model for the optimization problem.
    solver : cp.CpSolver
        The CP-SAT solver instance used to solve the model.
    vars : dict
        Dictionary to hold decision variables for the model.
    """

    def __init__(
            self,
            active_players: list[Player],
            history: HistoryManager,
            courts: list[Court],
            settings: Settings,
    ):
        """
        Initializes the ScrambleSolver with players, their history, and settings.

        Parameters
        ----------
        active_players : list[Player]
            List of players to be assigned to teams and matches.
        history : HistoryManager
            The history manager containing player histories.
        courts : list[Court]
            List of courts available for matches.
        settings : Settings
            The settings for the scramble solver.
        """
        self.active_players = active_players
        self._player_lookup = {player.id: player for player in active_players}
        self.history = history
        self.courts = courts
        self.settings = settings

        self.model = cp.CpModel()
        self.solver = cp.CpSolver()
        self.vars = {}

    def build_model(self):
        """
        Defines decision variables and structure needed for the optimization.
        Vars:
        - team: A dictionary mapping team player IDs to a boolean variable
            indicating if the team is in a match.
        - match: A dictionary mapping configurations of competing teams to a boolean variable
            indicating if they are in a match.
        """
        self.vars["team"] = {}
        self.vars["match"] = {}

        # create a variable for each team indicating if they are in a match
        self._build_team_vars()

        # create a variable for each configuration of competing teams indicating if they are in a match
        self._build_match_vars()

    def _build_match_vars(self):
        """
        Creates match variables for each possible configuration of teams.
        Match variables are created for combinations of teams that are disjoint,
        meaning no player is in more than one team in the match.
        """
        team_ids_list = list(self.vars["team"].keys())
        min_nr_teams = self.settings.min_nr_teams_in_match
        max_nr_teams = math.ceil(len(self.active_players) / min_nr_teams)
        for nr_teams in range(min_nr_teams, max_nr_teams + 1):
            for match_teams in combinations(team_ids_list, nr_teams):
                if not are_disjoint(match_teams):
                    continue
                ordered_match_teams = tuple(sorted(match_teams, key=lambda team: min(team)))
                if ordered_match_teams not in self.vars["match"]:
                    self.vars["match"][ordered_match_teams] = self.model.NewBoolVar(f"match_{ordered_match_teams}")

    def _build_team_vars(self):
        """
        Creates team variables for each possible player configuration
        based on the active players and their team sizes.
        Teams are pruned using a max-heap to keep only the best scoring teams.
        Teams are limited by:
        - Maximum number of teams per team size (MAX_TEAMS_PER_TEAM_SIZE).
        - Maximum number of teams per player (MAX_TEAMS_PER_PLAYER).
        """
        player_team_counts = {p.id: 0 for p in self.active_players}
        min_team_size = max(
            math.ceil(
                math.ceil(
                    len(self.active_players) / len(self.courts)
                ) / self.settings.min_nr_teams_in_match
            ),
            self.settings.min_team_size
        )
        max_team_size = min(
            math.ceil(len(self.active_players) / self.settings.min_nr_teams_in_match),
            2 * self.settings.min_team_size - 1
        )
        for nr_players in range(min_team_size, max_team_size + 1):
            top_k_heap = []  # max-heap for worst-first pruning

            for team_players in combinations(self.active_players, nr_players):
                score = score_team(list(team_players), self.history, self.settings)
                team_player_ids = tuple(sorted(player.id for player in team_players))

                self._try_add_team_to_heap(player_team_counts, score, team_player_ids, top_k_heap)

            for score, team_player_ids in top_k_heap:
                self.vars["team"][team_player_ids] = self.model.NewBoolVar(f"team_{team_player_ids}")

    @staticmethod
    def _try_add_team_to_heap(
            player_team_counts: dict[str, int],
            score: float,
            team_player_ids: tuple[int, ...],
            top_k_heap: list[tuple[float, tuple[str, ...]]]
    ):
        """
        Attempts to add a team to the max-heap of top K teams.
        If the heap is full or any player in the team has reached their maximum number of teams,
        it checks if the new team is better than the worst team in the heap.
        If so, it replaces the worst team with the new one.

        Parameters
        ----------
        player_team_counts : dict[str, int]
            Dictionary mapping player IDs to the number of teams they are part of.
        score : float
            The score of the team being considered for addition to the heap.
        team_player_ids : tuple[int, ...]
            Tuple of player IDs representing the team.
        top_k_heap : list[tuple[float, tuple[str, ...]]]
            The max-heap containing the top K teams, where each entry is a tuple of (score, team_player_ids).
        """
        MAX_TEAMS_PER_TEAM_SIZE = 1000
        MAX_TEAMS_PER_PLAYER = 30

        team_limit_reached = len(top_k_heap) >= MAX_TEAMS_PER_TEAM_SIZE
        any_player_at_limit = any(
            player_team_counts[pid] >= MAX_TEAMS_PER_PLAYER
            for pid in team_player_ids
        )
        if not team_limit_reached and not any_player_at_limit:
            # push if we don't yet have K teams
            heapq.heappush(top_k_heap, (-score, team_player_ids))
            for pid in team_player_ids:
                player_team_counts[pid] += 1
        else:
            # check if this team is better than the current worst
            if score < -top_k_heap[0][0]:  # note: top_k_heap[0][0] is negative
                # pop the worst team and push the new one
                _, worst_team = heapq.heappushpop(top_k_heap, (-score, team_player_ids))
                for pid in worst_team:
                    player_team_counts[pid] -= 1
                for pid in team_player_ids:
                    player_team_counts[pid] += 1

    def add_constraints(self):
        """
        Adds constraints to ensure valid match structure.
        Constraints:
        - Limit the number of matches to the number of courts.
        - Ensure each team is part of at most one match.
        - Ensure each player is in exactly one team.
        """
        # limit number of matches by the number of courts
        self.model.Add(sum(self.vars["match"].values()) <= len(self.courts))

        # team variable is True iff it’s part of some match
        for team_player_ids, team_var in self.vars["team"].items():
            matches_involving_team = [
                self.vars["match"][match_teams]
                for match_teams in self.vars["match"]
                if team_player_ids in match_teams
            ]
            if matches_involving_team:
                self.model.Add(team_var == sum(matches_involving_team))
            else:
                self.model.Add(team_var == 0)

        # each player is in exactly one team
        for player in self.active_players:
            teams_with_player = [
                self.vars["team"][team_player_ids]
                for team_player_ids in self.vars["team"]
                if player.id in team_player_ids
            ]
            self.model.Add(sum(teams_with_player) == 1)

    def set_objective(self):
        """
        Sets the weighted sum of scoring functions as the objective to minimize.
        """
        objective_terms = []
        for match_teams, match_var in self.vars["match"].items():
            # get the player IDs for the teams in this match
            team_player_ids_list = [list(team_player_ids) for team_player_ids in match_teams]
            # create a Match object from the team player IDs
            match = Match.from_team_player_ids(team_player_ids_list, self._player_lookup)
            # score the match using the scoring function
            score = score_match(match, self.history, self.settings)
            # add the score multiplied by the match variable to the objective
            objective_terms.append(score * match_var)

        # set the objective to minimize the total score
        self.model.Minimize(sum(objective_terms))

    def solve(self) -> Round:
        """
        Runs the solver and returns a Round object representing the optimized schedule.

        Returns
        -------
        Round
            A Round object containing the matches and resting players based on the optimized schedule.
        """
        self.build_model()
        self.add_constraints()
        self.set_objective()

        status = self.solver.Solve(self.model)

        if status in [cp.OPTIMAL, cp.FEASIBLE]:
            selected_matches = [
                match_teams
                for match_teams, match_var in self.vars["match"].items()
                if self.solver.Value(match_var) == 1
            ]
            matches = []
            for i, match_teams in enumerate(selected_matches):
                team_player_ids_list = [list(team_player_ids) for team_player_ids in match_teams]
                court = self.courts[i % len(self.courts)]
                match = Match.from_team_player_ids(team_player_ids_list, self._player_lookup, court)
                matches.append(match)
            return Round(matches)
        else:
            raise RuntimeError("No feasible solution found")
