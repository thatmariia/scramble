# external imports
from ortools.sat.python import cp_model as cp

import logging
import heapq
import math
from itertools import combinations
from scramble.core import Player, HistoryManager, Match, Court, Round, Team
from scramble.settings import Settings
from scramble.solver.utils import are_disjoint
from scramble.solver.scoring import score_match, score_team

LOGGER = logging.getLogger(__name__)

MAX_SCORE = 1_000_000

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

        self.num_to_court = {i: court for i, court in enumerate(self.courts)}
        self.num_to_player = {i+1: player for i, player in enumerate(self.active_players)}

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
        self.vars["partner_history"] = {}
        self.vars["opponent_history"] = {}
        self.vars["match"] = {}

        # add a match var for each court
        for i, court in self.num_to_court.items():
            self.vars["match"][i] = {}
            self.vars["match"][i]["uses_sum"] = self.model.NewIntVar(0, 6, f"match_{i}_uses_sum")
            self.vars["match"][i]["used_ok"] = self.model.NewBoolVar(f"match_{i}_used_ok")
            self.vars["match"][i]["unused_ok"] = self.model.NewBoolVar(f"match_{i}_unused_ok")

            self.vars["match"][i]["score"] = self.model.NewIntVar(0, MAX_SCORE, f"match_{i}_score")
            self.vars["match"][i]["teams"] = {}

            # max 3 teams per match?
            for j in range(3):
                self.vars["match"][i]["teams"][j] = {}
                self.vars["match"][i]["teams"][j]["use"] = self.model.NewBoolVar(f"match_{i}_teams_{j}_use")
                self.vars["match"][i]["teams"][j]["players"] = {}

                # max 3 players per team?
                for p in range(3):
                    self.vars["match"][i]["teams"][j]["players"][p] = {}
                    self.vars["match"][i]["teams"][j]["players"][p]["id"] = self.model.NewIntVar(0, len(self.num_to_player), f"match_{i}_team_{j}_player_{p}")
                    self.vars["match"][i]["teams"][j]["players"][p]["use"] = self.model.NewBoolVar(f"match_{i}_team_{j}_player_{p}_use")
                    self.vars["match"][i]["teams"][j]["players"][p]["div_score_partner"] = self.model.NewIntVar(0, MAX_SCORE, f"match_{i}_team_{j}_player_{p}_div_score_partner")

                    for q in range(3):
                        self.vars["match"][i]["teams"][j]["players"][p][f"div_score_opponent_{q}"] = self.model.NewIntVar(0, MAX_SCORE, f"match_{i}_team_{j}_player_{p}_div_score_opponent")

        self.partner_history = []
        self.opponent_history = []
        for p1, p2 in combinations(self.num_to_player.items(), 2):
            p1_id, p1 = p1
            p2_id, p2 = p2

            self.vars["partner_history"][(p1_id, p2_id)] = self.model.NewIntVar(0, MAX_SCORE, f"partner_history_{i}_{j}")
            self.vars["partner_history"][(p2_id, p1_id)] = self.model.NewIntVar(0, MAX_SCORE, f"partner_history_{j}_{i}")

            self.vars["opponent_history"][(p1_id, p2_id)] = self.model.NewIntVar(0, MAX_SCORE, f"opponent_history_{i}_{j}")
            self.vars["opponent_history"][(p2_id, p1_id)] = self.model.NewIntVar(0, MAX_SCORE, f"opponent_history_{i}_{j}")

            self.partner_history.append((p1_id, p2_id, self.history.get_partner_frequency(p1.id, p2.id)))
            self.partner_history.append((p2_id, p1_id, self.history.get_partner_frequency(p1.id, p2.id)))

            self.opponent_history.append((p1_id, p2_id, self.history.get_opponent_frequency(p1.id, p2.id)))
            self.opponent_history.append((p2_id, p1_id, self.history.get_opponent_frequency(p1.id, p2.id)))

        # add 0 diversity for not-used players
        for p_id in self.num_to_player.keys():
            self.partner_history.append((p_id, 0, 0))
            self.partner_history.append((0, p_id, 0))
            self.opponent_history.append((p_id, 0, 0))
            self.opponent_history.append((0, p_id, 0))
        self.partner_history.append((0, 0, 0))
        self.opponent_history.append((0, 0, 0))

        LOGGER.debug(f"build match vars, len={ScrambleSolver.count_vars(self.vars)}")

    @staticmethod
    def count_vars(d: dict):
        count = 0
        for v in d.values():
            if isinstance(v, dict):
                count += ScrambleSolver.count_vars(v)
            else:
                count += 1
        return count

    def add_constraints(self):
        """
        Adds constraints to ensure valid match structure.
        Constraints:
        - Limit the number of matches to the number of courts.
        - Ensure each team is part of at most one match.
        - Ensure each player is in exactly one team.
        """
        for match in self.vars["match"].values():
            for team in match["teams"].values():
                # compute if player is used
                for player_vars in team["players"].values():
                    player = player_vars["id"]
                    use = player_vars["use"]
                    self.model.Add(player > 0).OnlyEnforceIf(use)
                    self.model.Add(player == 0).OnlyEnforceIf(use.Not())

                # compute if team is used (i.e. minimum 2 teams)
                players = [player["use"] for player in team["players"].values()]
                use = team["use"]
                self.model.Add(sum(players) >= 2).OnlyEnforceIf(use)
                self.model.Add(sum(players) == 0).OnlyEnforceIf(use.Not())

        all_players =  [
                player
                for match in self.vars["match"].values()
                for team in match["teams"].values()
                for player in team["players"].values()
            ]
        # ensure no player is used twice
        for a, b in combinations(all_players, 2):
            self.model.Add(a["id"] != b["id"]).OnlyEnforceIf(a["use"])

        # ensure every player is used
        expected_sum = sum(i + 1 for i in range(len(self.active_players)))
        all_player_ids = [player["id"] for player in all_players]
        self.model.Add(sum(all_player_ids) == expected_sum)

        LOGGER.debug(f"num_players={len(self.active_players)}, expected_sum={expected_sum}")

        # every team has at least 2 teams
        for match in self.vars["match"].values():
            team_uses = [
                team["use"]
                for team in match["teams"].values()
            ]

            self.model.Add(match["uses_sum"] == sum(team_uses))

            # Reify the conditions
            self.model.Add(match["uses_sum"] == 0).OnlyEnforceIf(match["unused_ok"])
            self.model.Add(match["uses_sum"] != 0).OnlyEnforceIf(match["unused_ok"].Not())

            self.model.Add(match["uses_sum"] >= 2).OnlyEnforceIf(match["used_ok"])
            self.model.Add(match["uses_sum"] < 2).OnlyEnforceIf(match["used_ok"].Not())

            # Enforce match not used or >= 2 teams
            self.model.AddBoolOr([match["unused_ok"], match["used_ok"]])

    def set_objective(self):
        """
        Sets the weighted sum of scoring functions as the objective to minimize.
        """

        for match in self.vars["match"].values():
            teams = match["teams"]

            players =  [
                player
                for team in teams.values()
                for player in team["players"].values()
                ]

            # diversity partner score:
            for team in teams.values():
                for p1, p2 in combinations(team["players"].values(), 2):
                    self.model.AddAllowedAssignments([p1["id"], p2["id"], p1["div_score_partner"]], self.partner_history)

            # diversity opponent score:
            for t1, t2 in combinations(match["teams"].values(), 2):
                for p1 in t1["players"].values():
                    for i, p2 in t2["players"].items():
                        self.model.AddAllowedAssignments([p1["id"], p2["id"], p1[f"div_score_opponent_{i}"]], self.opponent_history)

            div_score_partner = [player["div_score_partner"] for player in players]
            div_score_opponent = [player[f"div_score_opponent_{i}"] for player in players for i in range(3)]
            self.model.Add(match["score"] == sum([sum(div_score_partner), sum(div_score_opponent)]))

        score = [match["score"] for match in self.vars["match"].values()]
        self.model.Minimize(sum(score))

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
            matches = []
            for i, match in self.vars["match"].items():
                print(f"match: score={self.solver.Value(match["score"])}")

                def add_if_exists(team, num):
                    if num == 0:
                        return
                    team.append(self.num_to_player[num])

                teams = []
                for team in match["teams"].values():
                    players = []
                    for player in team["players"].values():
                        add_if_exists(players, self.solver.Value(player["id"]))

                    if len(players) > 0:
                        teams.append(Team(players))

                if len(teams) > 0:
                    match = Match(teams, self.courts[i])
                    matches.append(match)

            return Round(matches)
        else:
            raise RuntimeError("No feasible solution found")
