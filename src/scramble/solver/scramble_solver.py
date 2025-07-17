# external imports
from ortools.sat.python import cp_model as cp
from ortools.sat.python.cp_model import IntVar

import logging
import math
import multiprocessing
from scramble.core import Player, Team, HistoryManager, Match, Court, Round
from scramble.settings import Settings, Goal
from scramble.solver.model_variables import ModelVariables
from scramble.solver.hints import add_startup_hints, add_hints_from_round
from scramble.solver.constraints import add_constraints, add_symmetry_breaking
from scramble.solver.objective import score_round
from scramble.solver.objective.scoring_functions import SCORING_FUNCTIONS
from scramble.solver.utils import define_and_var

LOGGER = logging.getLogger(__name__)


class InspectObjective(cp.CpSolverSolutionCallback):
    def __init__(self, mdl, mv, scorers):
        super().__init__()
        self._mdl = mdl
        self._mv = mv
        self._scorers = scorers

    def on_solution_callback(self):
        vals = {}
        for name, fn in self._scorers.items():
            v = self.Value(fn(self._mdl, self._mv))
            vals[name] = v
        print(f"obj={self.ObjectiveValue()}  ", vals, flush=True)


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
            prev_round: Round | None = None
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
        self.active_players = sorted(active_players, key=lambda p: p.level.value)
        self.history = history
        self.courts = sorted(courts, key=lambda c: c.id)
        self.settings = settings

        if len(courts) == 0:
            raise ValueError("Courts may not be empty")

        if  len({player.id for player in active_players}) != len(active_players):
            raise ValueError("Player IDs must be unique")

        if len({court.id for court in courts}) != len(courts):
            raise ValueError("Court IDs must be unique")

        self.model = cp.CpModel()
        self.solver = cp.CpSolver()
        self.solver.parameters.log_search_progress = True
        self.solver.parameters.num_search_workers = min(8, multiprocessing.cpu_count())
        self.solver.parameters.random_seed = 1
        # self.solver.parameters.linearization_level = 1
        # self.solver.parameters.max_presolve_iterations = 2
        # self.solver.parameters.max_time_in_seconds = 60.0
        self.vars = {}
        self.nr_teams = max(
            self.settings.min_nr_teams_in_match,
            math.ceil(len(self.active_players) / self.settings.min_team_size)
        )
        self._mv = None
        self._prev_round = prev_round
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
        self.vars["team_size"] = {}

        flat_vars_player_in_team = []
        flat_vars_team_on_court = []
        flat_vars_team_active = []
        flat_vars_court_active = []
        flat_vars_team_size = []

        for team_id in range(self.nr_teams):
            self.vars["team_size"][team_id] = self.model.new_int_var(
                0, self.settings.max_team_size, f"team_size_{team_id}"
            )
            flat_vars_team_size.append(self.vars["team_size"][team_id])
            for player in self.active_players:
                self.vars["player_in_team"][(player.id, team_id)] = self.model.new_bool_var(
                    f"player_{player.id}_in_team_{team_id}"
                )
                flat_vars_player_in_team.append(self.vars["player_in_team"][(player.id, team_id)])
            for court in self.courts:
                self.vars["team_on_court"][(team_id, court.id)] = self.model.new_bool_var(
                    f"team_{team_id}_on_court_{court.id}"
                )
                flat_vars_team_on_court.append(self.vars["team_on_court"][(team_id, court.id)])
            self.vars["team_active"][team_id] = self.model.new_bool_var(
                f"team_{team_id}_active"
            )
            flat_vars_team_active.append(self.vars["team_active"][team_id])

        for court in self.courts:
            self.vars["court_active"][court.id] = self.model.new_bool_var(
                f"court_{court.id}_active"
            )
            flat_vars_court_active.append(self.vars["court_active"][court.id])

        flat_vars = [flat_vars_player_in_team, flat_vars_team_on_court, flat_vars_team_active, flat_vars_court_active, flat_vars_team_size]
        max_len = max(len(v) for v in flat_vars)
        flat_vars_zigzag = []
        for i in range(max_len):
            for var_list in flat_vars:
                if i < len(var_list):
                    flat_vars_zigzag.append(var_list[i])

        # self.model.add_decision_strategy(
        #     variables=flat_vars_zigzag,
        #     var_strategy=cp.CHOOSE_MIN_DOMAIN_SIZE,
        #     domain_strategy=cp.SELECT_MAX_VALUE
        # )

        LOGGER.debug(
            f"number of vars: {self.nr_teams * (len(self.active_players) + len(self.courts) + 1) + len(self.courts)}")

    def build_mv(self):
        self._mv = ModelVariables(
            player_in_team=self.vars["player_in_team"],
            team_on_court=self.vars["team_on_court"],
            team_active=self.vars["team_active"],
            court_active=self.vars["court_active"],
            team_size=self.vars["team_size"],
            nr_teams=self.nr_teams,
            active_players=self.active_players,
            courts=self.courts,
            history=self.history,
            settings=self.settings,
        )

    def add_hints(self):
        add_startup_hints(self.model, self._mv)
        # if self._prev_round:
        #     add_hints_from_round(self.model, self._mv, self._prev_round)
        # else:
        #     add_startup_hints(self.model, self._mv)

    def add_constraints(self):
        """
        Adds constraints to ensure valid match structure.
        """
        add_constraints(self.model, self._mv)
        add_symmetry_breaking(self.model, self._mv)

    def set_objective(self):
        """
        Sets the weighted sum of scoring functions as the objective to minimize.
        """
        self.model.Minimize(score_round(self.model, self._mv))

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
        self.build_mv()
        self.add_hints()
        self.add_constraints()
        self.set_objective()

        status = self.solver.Solve(self.model, InspectObjective(self.model, self._mv, SCORING_FUNCTIONS))

        if status in [cp.OPTIMAL, cp.FEASIBLE]:
            matches = self._matches_from_solutions()
            game_round = Round(matches)
            LOGGER.debug(f"Solution found:\n{game_round}")
            # print(self.solver.ResponseStats())
            return game_round
        else:
            raise RuntimeError("No feasible solution found")
