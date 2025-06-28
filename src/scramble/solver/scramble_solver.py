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
    active_players : list[Player]
        List of players to be assigned to teams and matches.
    resting_players : list[Player]
        List of players who are resting and should not be assigned to matches.
    _player_lookup : dict[int, Player]
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
            resting_players: list[Player],
            history: HistoryManager,
            fields: list[Field],
            settings: Settings,
    ):
        """
        Initializes the ScrambleSolver with players, their history, and settings.

        Parameters
        ----------
        active_players : list[Player]
            List of players to be assigned to teams and matches.
        resting_players : list[Player]
            List of players who are resting and should not be assigned to matches.
        history : HistoryManager
            The history manager containing player histories.
        fields : list[Field]
            List of fields available for matches.
        settings : Settings
            The settings for the scramble solver.
        """
        self.active_players = active_players
        self.resting_players = resting_players
        self._player_lookup = {player.id: player for player in active_players + resting_players}
        self.history = history
        self.fields = fields
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
        for team_players in combinations(self.active_players, self.settings.team_size):
            team_player_ids = tuple(sorted(player.id for player in team_players))
            self.vars["team"][team_player_ids] = self.model.NewBoolVar(f"team_{team_player_ids}")

        # create a variable for each configuration of competing teams
        # indicating if they are in a match
        team_ids_list = list(self.vars["team"].keys())
        for nr_teams in range(self.settings.min_nr_teams_in_match, len(self.active_players) + 1):
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
        self.model.Add(sum(self.vars["match"].values()) <= len(self.fields))

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
                field = self.fields[i % len(self.fields)]
                match = Match.from_team_player_ids(team_player_ids_list, self._player_lookup, field)
                matches.append(match)
            return Round(matches=matches, resting_players=self.resting_players)
        else:
            raise RuntimeError("No feasible solution found")
