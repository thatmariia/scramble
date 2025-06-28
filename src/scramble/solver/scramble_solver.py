# external imports
from ortools.sat.python import cp_model as cp

from itertools import combinations
from scramble.core import Player, HistoryManager, Match, Field, Round
from scramble.settings import Settings
from scramble.solver.utils import are_disjoint
from scramble.solver.scoring import score_match


class ScrambleSolver:
    """
    Responsible for solving the scramble scheduling problem using OR-Tools CP-SAT solver,
    aka Constraint Programming Solver.
    This class defines the optimization model, adds constraints, and sets the objective function
    based on scoring functions.

    Attributes
    ----------
    players : list[Player]
        List of players to be assigned to teams and matches.
    _player_lookup : dict[int, Player]
        Dictionary mapping player IDs to Player objects for quick access.
    history : HistoryManager
        The history manager containing player histories.
    settings : Settings
        The settings for the scramble solver.
    resting_player_ids : set[int] | None
        Optional set of player IDs who should not be assigned to matches.
    nonresting_player_ids : set[int]
        Set of player IDs who are eligible to play (not resting).
    model : cp.CpModel
        The CP-SAT model for the optimization problem.
    solver : cp.CpSolver
        The CP-SAT solver instance used to solve the model.
    vars : dict
        Dictionary to hold decision variables for the model.
    """

    def __init__(
            self,
            players: list[Player],
            history: HistoryManager,
            settings: Settings,
            resting_player_ids: set[int] | None = None,
    ):
        """
        Initializes the ScrambleSolver with players, their history, and settings.

        Parameters
        ----------
        players : list[Player]
            List of players to be assigned to teams and matches.
        history : HistoryManager
            The history manager containing player histories.
        settings : Settings
            The settings for the scramble solver.
        resting_player_ids : set[int] | None
            Optional set of player IDs who should not be assigned to matches.
            If None, all players are considered for matches.
        """
        self.players = players
        self._player_lookup = {player.id: player for player in players}
        self.history = history
        self.settings = settings
        self.resting_player_ids = resting_player_ids or set()
        self.nonresting_player_ids = set(
            player.id for player in self.players if player.id not in self.resting_player_ids
        )

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
        for team_player_ids in combinations(self.nonresting_player_ids, self.settings.team_size):
            self.vars["team"][team_player_ids] = self.model.NewBoolVar(f"team_{team_player_ids}")

        # create a variable for each configuration of competing teams
        # indicating if they are in a match
        team_ids_list = list(self.vars["team"].keys())
        for nr_teams in range(self.settings.min_nr_teams_in_match, len(self.nonresting_player_ids) + 1):
            for match_teams in combinations(team_ids_list, nr_teams):
                if not are_disjoint(match_teams):
                    continue
                ordered_match_teams = tuple(sorted(match_teams, key=lambda team: min(team)))
                if ordered_match_teams not in self.vars["match"]:
                    self.vars["match"][ordered_match_teams] = self.model.NewBoolVar(f"match_{ordered_match_teams}")

    def add_constraints(self):
        """
        Adds constraints to ensure valid match structure.
        Constraints:
        - Limit the number of matches to the number of fields.
        - Ensure each team is part of at most one match.
        - Ensure each player is in exactly one team.
        """

        # limit number of matches by the number of fields
        self.model.Add(sum(self.vars["match"].values()) <= self.settings.nr_fields)

        # team variable is True iff it’s part of some match
        for team_player_ids, team_var in self.vars["team"].items():
            matches_involving_team = [
                self.vars["match"][match_teams]
                for match_teams in self.vars["match"]
                if team_player_ids in match_teams
            ]
            if matches_involving_team:
                self.model.Add(team_var == sum(matches_involving_team))

        # each player is in exactly one team
        for player_id in self.nonresting_player_ids:
            teams_with_player = [
                self.vars["team"][team_player_ids]
                for team_player_ids in self.vars["team"]
                if player_id in team_player_ids
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
            score = score_match(match, self.history, self.settings.goal_configs)
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
                # TODO: select fields instead of creating them
                field = Field(id=i, name=f"Field {i + 1}")
                match = Match.from_team_player_ids(team_player_ids_list, self._player_lookup, field)
                matches.append(match)
            resting_players = [self._player_lookup[player_id] for player_id in self.resting_player_ids]
            return Round(matches=matches, resting_players=resting_players)
        else:
            raise RuntimeError("No feasible solution found")
