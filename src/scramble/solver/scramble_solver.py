# external imports
from ortools.sat.python import cp_model as cp

import logging
import math
from scramble.core import Player, Team, HistoryManager, Match, Court, Round
from scramble.settings import Settings, Goal
from scramble.solver.model_variables import ModelVariables
from scramble.solver.constraints import add_constraints, add_symmetry_breaking
from scramble.solver.objective import score_round

LOGGER = logging.getLogger(__name__)


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
    nr_teams : int
        The max number of teams to be created based on the number of players and settings.
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
        self.history = history
        self.courts = courts
        self.settings = settings

        self.model = cp.CpModel()
        self.solver = cp.CpSolver()
        self.vars = {}
        max_nr_teams_on_court = math.ceil(len(self.active_players) / self.settings.min_team_size)
        self.nr_teams = max(
            self.settings.min_nr_teams_in_match,
            len(self.courts) * max_nr_teams_on_court
        )
        LOGGER.debug(f"number of teams: {self.nr_teams}")

    def build_model(self):
        """
        Defines decision variables and structure needed for the optimization.
        Vars:
        - player_in_team[(player_id, team_id)]: Bool var indicating if player is in a team.
        - team_on_court[(team_id, court_id)]: Bool var indicating if a team is on a court.
        - team_active[team_id]: Bool var indicating if a team is active (has players).
        """
        self.vars["player_in_team"] = {}
        self.vars["team_on_court"] = {}
        self.vars["team_active"] = {}
        self.vars["court_active"] = {}

        for team_id in range(self.nr_teams):
            for player in self.active_players:
                self.vars["player_in_team"][(player.id, team_id)] = self.model.new_bool_var(
                    f"player_{player.id}_in_team_{team_id}"
                )
            for court in self.courts:
                self.vars["team_on_court"][(team_id, court.id)] = self.model.new_bool_var(
                    f"team_{team_id}_on_court_{court.id}"
                )
            self.vars["team_active"][team_id] = self.model.new_bool_var(
                f"team_{team_id}_active"
            )

        for court in self.courts:
            self.vars["court_active"][court.id] = self.model.new_bool_var(
                f"court_{court.id}_active"
            )

        LOGGER.debug(f"number of vars: {self.nr_teams * (len(self.active_players) + len(self.courts) + 1) + len(self.courts)}")

        # LOGGER.debug(f"vars: player_in_team={self.vars['player_in_team']}, ")
        # LOGGER.debug(f"vars: team_on_court={self.vars['team_on_court']}, ")
        # LOGGER.debug(f"vars: team_active={self.vars['team_active']}")

    def add_constraints(self):
        """
        Adds constraints to ensure valid match structure.
        """
        mv = ModelVariables(
            player_in_team=self.vars["player_in_team"],
            team_on_court=self.vars["team_on_court"],
            team_active=self.vars["team_active"],
            court_active=self.vars["court_active"],
            nr_teams=self.nr_teams,
            active_players=self.active_players,
            courts=self.courts,
            history=self.history,
            settings=self.settings,
        )
        add_constraints(self.model, mv)
        add_symmetry_breaking(self.model, mv)

    def set_objective(self):
        """
        Sets the weighted sum of scoring functions as the objective to minimize.
        """
        self.model.Minimize(score_round(
            self.model,
            ModelVariables(
                player_in_team=self.vars["player_in_team"],
                team_on_court=self.vars["team_on_court"],
                team_active=self.vars["team_active"],
                court_active=self.vars["court_active"],
                nr_teams=self.nr_teams,
                active_players=self.active_players,
                courts=self.courts,
                history=self.history,
                settings=self.settings,
            )
        ))

    def _matches_from_solutions(self) -> list[Match]:
        """
        Constructs Match objects based on the solved variables.

        Returns
        -------
        list[Match]
            List of matches created from selected teams and players.
        """
        # collect players into teams
        all_teams: dict[int, Team] = {}

        for team_id in range(self.nr_teams):
            team_players = [
                player for player in self.active_players
                if self.solver.Value(self.vars["player_in_team"][player.id, team_id])
            ]
            if team_players:
                all_teams[team_id] = Team(team_players)

        # group teams by court assignment
        teams_on_courts: dict[str, list[Team]] = {}
        courts_lookup = {court.id: court for court in self.courts}

        for court in self.courts:
            court_teams = [
                team for team_id, team in all_teams.items()
                if self.solver.Value(self.vars["team_on_court"][team_id, court.id])
            ]
            if court_teams:
                teams_on_courts[court.id] = court_teams

        # build Match objects
        matches = [
            Match(teams, courts_lookup[court_id]) for court_id, teams in teams_on_courts.items()
        ]

        return matches

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
            matches = self._matches_from_solutions()
            game_round = Round(matches)
            LOGGER.debug(f"Solution found:\n{game_round}")
            return game_round
        else:
            raise RuntimeError("No feasible solution found")
