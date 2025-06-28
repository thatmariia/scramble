# external imports
from ortools.sat.python import cp_model as cp

from scramble.core import Player, HistoryManager, Round
from scramble.settings import Settings
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
    history : HistoryManager
        The history manager containing player histories.
    settings : Settings
        The settings for the scramble solver.
    resting_player_ids : set[int] | None
        Optional set of player IDs who should not be assigned to matches.
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
        self.history = history
        self.settings = settings
        self.resting_player_ids = resting_player_ids or set()

        self.model = cp.CpModel()
        self.solver = cp.CpSolver()
        self.vars = {}

    def build_model(self):
        """
        Defines decision variables and structure needed for the optimization.
        """
        # TODO: Create boolean/int vars for team memberships, match assignments, etc.
        pass

    def add_constraints(self):
        """
        Adds constraints to ensure valid match structure.
        """
        # TODO: Add constraints like:
        #  - each player plays at most once
        #  - valid team sizes
        #  - valid match sizes
        #  - field limits
        pass

    def set_objective(self):
        """
        Sets the weighted sum of scoring functions as the objective to minimize.
        """
        # TODO: Use score_match to build a cost expression
        pass

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
            # TODO: extract assignments and build Round
            return Round(matches=[], resting_players=[])
        else:
            raise RuntimeError("No feasible solution found")
