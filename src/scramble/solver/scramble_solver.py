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
from scramble.solver.objective import score_round, get_lb, get_ub
from scramble.solver.objective.scoring_functions import SCORING_FUNCTIONS
from scramble.solver.utils import define_and_var

LOGGER = logging.getLogger(__name__)


class SolutionPrinter(cp.CpSolverSolutionCallback):
    def __init__(self):
        cp.CpSolverSolutionCallback.__init__(self)
        self.best_objective = None

    def on_solution_callback(self):
        obj = self.objective_value
        if self.best_objective is None or obj < self.best_objective:
            print(f'New best objective: {obj}')
            self.best_objective = obj


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
        self.solver.parameters.num_search_workers = max(8, multiprocessing.cpu_count())
        self.solver.parameters.random_seed = 1
        self.solver.parameters.linearization_level = 2
        self.solver.parameters.cut_level = 2
        self.solver.parameters.add_lp_constraints_lazily = True
        self.solver.parameters.add_objective_cut = True
        self.solver.parameters.add_cg_cuts = True
        self.solver.parameters.add_mir_cuts = True
        self.solver.parameters.add_zero_half_cuts = True
        self.solver.parameters.add_clique_cuts = True
        self.solver.parameters.add_rlt_cuts = True
        self.solver.parameters.add_lin_max_cuts = True
        self.solver.parameters.use_implied_bounds = True
        # self.solver.parameters.optimize_with_core = True
        self.solver.parameters.optimize_with_lb_tree_search = True
        self.solver.parameters.exploit_relaxation_solution = True
        self.solver.parameters.symmetry_level = 4
        self.solver.parameters.new_linear_propagation = True
        self.solver.parameters.use_symmetry_in_lp = True
        self.solver.parameters.exploit_best_solution = True
        self.solver.parameters.only_solve_ip = True
        # self.solver.parameters.mip_compute_true_objective_bound = True
        self.solver.parameters.randomize_search = True

        # self.solver.parameters.max_num_cuts = 100000

        # optionally: params.find_feasible_solution_period = 0
        # self.solver.parameters.max_time_in_seconds = 10  # 10 seconds for example

        self.solver.parameters.search_branching = cp.PORTFOLIO_WITH_QUICK_RESTART_SEARCH

        self.vars = {}
        self.nr_teams = max(
            self.settings.min_nr_teams_in_match,
            math.ceil(len(self.active_players) / self.settings.min_team_size)
        )
        print("nr teams:", self.nr_teams)
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

        flat_vars = flat_vars_team_active + flat_vars_court_active + flat_vars_player_in_team + flat_vars_team_on_court + flat_vars_team_size
        self.model.add_decision_strategy(
            variables=flat_vars,
            var_strategy=cp.CHOOSE_FIRST,
            domain_strategy=cp.SELECT_MAX_VALUE
        )

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
        self.model.minimize(score_round(self.model, self._mv))

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

        # status = self.solver.Solve(self.model)
        printer = SolutionPrinter()
        status = self.solver.solve(self.model, solution_callback=printer)

        if status in [cp.OPTIMAL, cp.FEASIBLE]:
            matches = self._matches_from_solutions()
            game_round = Round(matches)
            LOGGER.debug(f"Solution found:\n{game_round}")
            print(self.solver.response_stats())
            return game_round
        else:
            raise RuntimeError("No feasible solution found")
