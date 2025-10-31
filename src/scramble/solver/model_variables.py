from dataclasses import dataclass
from collections import Counter
import math
import operator
from abc import ABC, abstractmethod
from ortools.sat.python.cp_model import IntVar
from ortools.sat.python import cp_model as cp
from scramble.settings import Settings
from scramble.core import Player, HistoryManager, Court
from scramble.solver.utils import define_and_var, define_and_var_imp, define_or_var, reify_with_fallback, reify_existing_with_fallback, reify_existing_with_inequality
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
    team_size: dict
    nr_teams: int
    active_players: list[Player]
    courts: list[Court]
    history: HistoryManager
    settings: Settings
    id_to_player: dict[str, Player] = None
    _player_ids: list[str] = None
    _teams_same_court_cache = None
    _players_same_court_diff_teams_cache = None
    _players_same_court_cache = None
    _players_same_team_cache = None
    _player_on_court_cache = None
    _player_team_on_court_cache = None
    _court_lvl_spread_cache = None
    _scaled_avg_team_lvl_cache = None
    _team_has_lvl_cache = None
    _team_level_range_cache = None

    def __post_init__(self):
        self._player_ids = [player.id for player in self.active_players]
        self.id_to_player = {player.id: player for player in self.active_players}
        self.scale_weights()
        self._teams_same_court_cache = {}
        self._players_same_court_diff_teams_cache = {}
        self._players_same_court_cache = {}
        self._players_same_team_cache = {}
        self._player_on_court_cache = {}
        self._player_team_on_court_cache = {}
        self._court_lvl_spread_cache = {}
        self._scaled_avg_team_lvl_cache = {}
        self._team_has_lvl_cache = {}
        self._team_level_range_cache = {}

    def scale_weights(self):
        def scale_weight(w_value, w_c):
            if w_c == 0:
                return 0
            return int(w_value * w_c)

        ubc = UpperBoundsComputer(self)
        weight_coefs = ubc.compute_weight_coefs()
        for goal, config in self.settings.goal_configs.items():
            if config.enabled:
                weight_coef = weight_coefs[goal]
                config.weight = scale_weight(config.weight, weight_coef)
            else:
                config.weight = 0
            if config.weight == 0:
                config.enabled = False
            # print("Scaled Weight for goal", goal.value, ":", config.weight)

    def team_has_lvl(self, mdl: cp, team_id: int, lvl: Level) -> IntVar:
        """
        Returns a BoolVar that is true iff the team has at least one player with the given level.
        """
        key = (team_id, lvl)
        if key in self._team_has_lvl_cache:
            return self._team_has_lvl_cache[(team_id, lvl)]

        lits = [
            self.player_in_team[(p.id, team_id)]
            for p in self.active_players
            if p.level.value == lvl
        ]

        if not lits:
            has = mdl.new_bool_var(f"t{team_id}_has_no_{lvl}")
            mdl.add(has == 0)
            self._team_has_lvl_cache[key] = has
            return has

        if len(lits) == 1:
            has = lits[0]
            self._team_has_lvl_cache[key] = has
            return has

        has = mdl.new_bool_var(f"t{team_id}_has_lvl_{lvl}")

        # mdl.add(sum(lits) >= 1).only_enforce_if(has)
        # mdl.add(sum(lits) == 0).only_enforce_if(has.Not())

        for lit in lits:
            mdl.add_implication(lit, has)
            mdl.add_implication(has.Not(), lit.Not())

        mdl.add_implication(has, self.team_active[team_id])
        mdl.add_implication(self.team_active[team_id].Not(), has.Not())

        self._team_has_lvl_cache[key] = has
        return has

    def team_level_range(self, mdl: cp, team_id: int) -> IntVar:
        """
        Returns a tuple of IntVars representing the minimum and maximum levels of the team with the given ID.
        """
        if team_id in self._team_level_range_cache:
            return self._team_level_range_cache[team_id]

        levels = sorted({p.level.value for p in self.active_players})
        if len(set(levels)) == 1:
            const = mdl.new_int_var(0, 0, f"rng_t{team_id}")
            self._team_level_range_cache[team_id] = const
            return const

        rng = mdl.new_int_var(0, levels[-1] - levels[0], f"rng_t{team_id}")
        mdl.add(rng == 0).only_enforce_if(self.team_active[team_id].Not())
        has = {lvl: self.team_has_lvl(mdl, team_id, lvl) for lvl in levels}

        for i, lo in enumerate(levels):
            for hi in levels[i + 1:]:
                both = mdl.new_bool_var(f"t{team_id}_lvl{lo}_{hi}_both")
                mdl.add(has[lo] + has[hi] == 2).only_enforce_if(both)
                mdl.add(has[lo] + has[hi] <= 1).only_enforce_if(both.Not())

                mdl.add(rng >= hi - lo).only_enforce_if(both)

        self._team_level_range_cache[team_id] = rng
        return rng

    def court_lvl_spread(self, mdl: cp, court_id: str) -> IntVar:
        if court_id in self._court_lvl_spread_cache:
            return self._court_lvl_spread_cache[court_id]

        max_lvl = max(p.level.value for p in self.active_players)
        min_lvl = min(p.level.value for p in self.active_players)
        lcm_sizes = self.settings.lcm_sizes()
        scaled_max_lvl = lcm_sizes * max_lvl
        scaled_min_lvl = lcm_sizes * min_lvl

        avg_team_lvls = []
        for team_id in range(self.nr_teams):
            on_court = self.team_on_court[(team_id, court_id)]
            mdl.add_implication(on_court, self.team_active[team_id])
            avg_team_lvls.append((on_court, self.scaled_avg_team_lvl(mdl, team_id)))

        max_lvl = mdl.new_int_var(scaled_min_lvl, scaled_max_lvl, f"max_lvl_{court_id}")
        min_lvl = mdl.new_int_var(scaled_min_lvl, scaled_max_lvl, f"min_lvl_{court_id}")

        for present, lvl in avg_team_lvls:
            mdl.add(max_lvl >= lvl).only_enforce_if(present)
            mdl.add(min_lvl <= lvl).only_enforce_if(present)

        court_spread = reify_with_fallback(
            mdl, max_lvl - min_lvl, 0, self.court_active[court_id],
            (0, scaled_max_lvl), f"court_spread_{court_id}"
        )
        self._court_lvl_spread_cache[court_id] = court_spread
        return court_spread

    def scaled_avg_team_lvl(self, mdl: cp, team_id: int) -> IntVar:
        """
        Returns a scaled average level of the team with the given ID.
        The scaling is done to ensure that the average level is an integer.
        """
        if team_id in self._scaled_avg_team_lvl_cache:
            return self._scaled_avg_team_lvl_cache[team_id]

        lcm_sizes = self.settings.lcm_sizes()

        total_domain_values: set[int] = set([0] + [lcm_sizes * p.level.value * s for p in self.active_players for s in range(self.settings.min_team_size, self.settings.max_team_size + 1)])
        total_domain = cp.Domain.from_values(sorted(total_domain_values))
        total_team_lvl = mdl.new_int_var_from_domain(total_domain, f"total_team_lvl_t{team_id}")

        mdl.add(total_team_lvl == lcm_sizes * sum(player.level * self.player_in_team[(player.id, team_id)] for player in self.active_players))

        avg_domain_values: set[int] = set([v // s for v in total_domain_values for s in range(self.settings.min_team_size, self.settings.max_team_size + 1)])
        avg_domain = cp.Domain.from_values(sorted(avg_domain_values))
        avg_team_lvl = mdl.new_int_var_from_domain(avg_domain, f"avg_team_lvl_t{team_id}")

        mdl.add_multiplication_equality(total_team_lvl, avg_team_lvl, self.team_size[team_id])
        mdl.add(avg_team_lvl == 0).only_enforce_if(self.team_active[team_id].Not())
        mdl.add(avg_team_lvl >= lcm_sizes * Level.min_value()).only_enforce_if(self.team_active[team_id])

        mdl.add(total_team_lvl == 0).only_enforce_if(self.team_active[team_id].Not())
        mdl.add(avg_team_lvl == 0).only_enforce_if(self.team_active[team_id].Not())

        self._scaled_avg_team_lvl_cache[team_id] = avg_team_lvl
        return avg_team_lvl

    def player_exists(self, player_id: str) -> bool:
        """
        Checks if a player with the given ID exists in the model variables.

        Parameters
        ----------
        player_id : str
            The ID of the player to check.

        Returns
        -------
        bool
            True if the player exists, False otherwise.
        """
        return player_id in self._player_ids

    def teams_on_same_court(self, mdl: cp, t1: int, t2: int):
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

    def players_in_same_team(self, mdl: cp, p1_id: str, p2_id: str) -> IntVar:
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

    def players_in_same_court_diff_team(self, mdl: cp, p1_id: str, p2_id: str) -> IntVar:
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

    def _players_on_same_court(self, mdl: cp, p1_id: str, p2_id: str) -> IntVar:
        key = tuple(sorted((p1_id, p2_id)))
        if key in self._players_same_court_cache:
            return self._players_same_court_cache[key]

        var = define_or_var(
            mdl,
            f"{p1_id}_{p2_id}_same_court",
            [
                define_and_var(
                    mdl,
                    f"{p1_id}_{p2_id}_both_on_{c.id}",
                    [self._player_on_court(mdl, p1_id, c.id), self._player_on_court(mdl, p2_id, c.id)]
                )
                for c in self.courts
            ]
        )
        self._players_same_court_cache[key] = var
        return var

    def _player_on_court(self, mdl: cp, player_id: str, court_id: str) -> IntVar:
        """
        Returns a BoolVar that is true iff the player is on the given court.
        """
        key = (player_id, court_id)
        if key in self._player_on_court_cache:
            return self._player_on_court_cache[key]

        per_team_lits = []
        for team_id in range(self.nr_teams):
            and_key = (player_id, team_id, court_id)
            if and_key not in self._player_team_on_court_cache:
                self._player_team_on_court_cache[and_key] = define_and_var(
                    mdl,
                    f"{player_id}_t{team_id}_on_c{court_id}",
                    [self.player_in_team[(player_id, team_id)],
                     self.team_on_court[(team_id, court_id)]]
                )
            per_team_lits.append(self._player_team_on_court_cache[and_key])

        var = define_or_var(
            mdl,
            f"{player_id}_on_court_{court_id}",
            per_team_lits
        )
        self._player_on_court_cache[key] = var
        return var


class BoundsComputer:
    """
    Base class for computing bounds for optimization goals.
    This class defines the interface for computing bounds based on model variables.
    """

    def __init__(self, mv: ModelVariables):
        self.mv = mv

    def compute(self, goal: Goal) -> int:
        """
        Computes the upper bound for a specific goal.

        Parameters
        ----------
        goal : Goal
            The optimization goal for which to compute the upper bound.
        """
        if goal == Goal.KEEP_IDEAL_TEAM_SIZE:
            return self._compute_keep_ideal_team_size()
        if goal == Goal.BALANCE_LVL:
            return self._compute_balance_level()
        if goal == Goal.REDUCE_LVL_GAP:
            return self._compute_reduce_level_gap()
        if goal == Goal.DIVERSIFY_PARTNERS:
            return self._compute_diversify_partners()
        if goal == Goal.DIVERSIFY_OPPONENTS:
            return self._compute_diversify_opponents()
        if goal == Goal.MAXIMIZE_COURTS_USAGE:
            return self._compute_maximize_courts_usage()
        return 0

    @abstractmethod
    def _compute_keep_ideal_team_size(self) -> int:
        pass

    @abstractmethod
    def _compute_balance_level(self) -> int:
        pass

    @abstractmethod
    def _compute_reduce_level_gap(self) -> int:
        pass

    @abstractmethod
    def _compute_diversify_partners(self) -> int:
        pass

    @abstractmethod
    def _compute_diversify_opponents(self) -> int:
        pass

    @abstractmethod
    def _compute_maximize_courts_usage(self) -> int:
        pass


class UpperBoundsComputer(BoundsComputer):
    """
    Computes upper bounds for various optimization goals based on the provided model variables.
    This class is used to determine the maximum possible values for each goal in the optimization process.
    """

    def __init__(self, mv: ModelVariables):
        super().__init__(mv)

    def compute_weight_coefs(self) -> dict[Goal, int]:
        raw_ubs = {goal: self.compute(goal) for goal in self.mv.settings.goal_configs.keys()}
        # for goal, ub in raw_ubs.items():
        #     print("Upper bound for goal", goal.value, ":", ub)
        raw_ub_values: list[int] = list(raw_ubs.values())
        non_zero_raw_ub_values = [ub for ub in raw_ub_values if ub > 0]
        ub_lcm = math.lcm(*non_zero_raw_ub_values)
        lcm_scaled_ratios = [ub_lcm // ub if ub > 0 else 0 for ub in raw_ub_values]
        max_ratio = max(lcm_scaled_ratios) if lcm_scaled_ratios else 1

        # cp_max_int = 2**63 - 1  # maximum value for a 64-bit signed integer
        cp_max_int = 10 ** 15  # a practical limit for our use case, can be adjusted
        max_weight = max([cfg.weight for cfg in self.mv.settings.goal_configs.values()])
        max_objective_value: float = sum(lcm_scaled_ratios) * sum(raw_ub_values) * max_weight
        safe_ub = max_objective_value / 100
        scale = float(safe_ub) / max_ratio if max_ratio > 0 else 1
        scaled_ratios = {}
        # print("LCM of raw upper bounds:", ub_lcm)
        # print("Scale factor for upper bounds:", scale)
        for goal, ub in raw_ubs.items():
            scaled_ratios[goal] = max(1, int(ub_lcm * scale / ub)) if ub > 0 else 0

        min_non_zero_scaled_ratio = min(ratio for ratio in scaled_ratios.values() if ratio > 0) if scaled_ratios else 1.0
        nr_digits = len(str(min_non_zero_scaled_ratio))
        max_allowed_nr_digits = 1
        digits_to_remove = max(0, nr_digits - max_allowed_nr_digits)
        denom = 10 ** digits_to_remove
        updated_scaled_ratios = {
            goal: max(1, ratio // denom) if ratio > 0 else 0
            for goal, ratio in scaled_ratios.items()
        }
        return updated_scaled_ratios

    def _compute_keep_ideal_team_size(self) -> int:
        return self.mv.nr_teams * (self.mv.settings.max_team_size - self.mv.settings.min_team_size)
        # return self.mv.settings.max_team_size - self.mv.settings.min_team_size

    def _compute_balance_level(self) -> int:
        lcm_sizes = self.mv.settings.lcm_sizes()
        max_pl = max(p.level.value for p in self.mv.active_players)
        min_pl = min(p.level.value for p in self.mv.active_players)
        # return math.comb(self.mv.nr_teams, 2) * lcm_sizes * (max_pl - min_pl)
        return lcm_sizes * (max_pl - min_pl) * len(self.mv.courts)

    def _compute_reduce_level_gap(self) -> int:
        max_pl = max(p.level.value for p in self.mv.active_players)
        min_pl = min(p.level.value for p in self.mv.active_players)
        return self.mv.nr_teams * (max_pl - min_pl)
        # return max_pl - min_pl

    def _compute_diversify_partners(self) -> int:
        existing_tuples = [
            (i, j) for (i, j) in self.mv.history.partner_tuples
            if self.mv.player_exists(i) and self.mv.player_exists(j)
        ]
        return sum([
            self.mv.history.get_partner_frequency(i, j)
            for (i, j) in existing_tuples
        ])

    def _compute_diversify_opponents(self) -> int:
        existing_tuples = [
            (i, j) for (i, j) in self.mv.history.opponent_tuples
            if self.mv.player_exists(i) and self.mv.player_exists(j)
        ]
        return sum([
            self.mv.history.get_opponent_frequency(i, j)
            for (i, j) in existing_tuples
        ])

    def _compute_maximize_courts_usage(self) -> int:
        overload_per_court = self.mv.nr_teams - self.mv.settings.min_nr_teams_in_match
        return len(self.mv.courts) * overload_per_court
        # return overload_per_court


class LowerBoundsComputer(BoundsComputer):
    """
    Computes lower bounds for various optimization goals based on the provided model variables.
    This class is used to determine the minimum possible values for each goal in the optimization process.
    """

    def __init__(self, mv: ModelVariables):
        super().__init__(mv)

    def _compute_keep_ideal_team_size(self) -> int:
        return len(self.mv.active_players) % self.mv.settings.min_team_size

    def _compute_balance_level(self) -> int:
        return 0

    def _compute_reduce_level_gap(self) -> int:
        m = self.mv.settings.min_team_size
        M = self.mv.settings.max_team_size
        level_counts = Counter(p.level.value for p in self.mv.active_players)

        if len(level_counts) <= 1:
            return 0

        sorted_levels = sorted(level_counts)
        delta = min(b - a for a, b in zip(sorted_levels, sorted_levels[1:]))

        leftovers = sum(c % m for c in level_counts.values())
        mixed_teams_min = math.ceil(leftovers / M)
        return mixed_teams_min * delta

    def _compute_diversify_partners(self) -> int:
        freqs = [
            self.mv.history.get_partner_frequency(i, j)
            for (i, j) in self.mv.history.partner_tuples
            if self.mv.player_exists(i) and self.mv.player_exists(j)
        ]
        return min(freqs) if freqs else 0

    def _compute_diversify_opponents(self) -> int:
        freqs = [
            self.mv.history.get_opponent_frequency(i, j)
            for (i, j) in self.mv.history.opponent_tuples
            if self.mv.player_exists(i) and self.mv.player_exists(j)
        ]
        return min(freqs) if freqs else 0

    def _compute_maximize_courts_usage(self) -> int:
        max_nr_teams = math.ceil(len(self.mv.active_players) / self.mv.settings.min_team_size)
        max_nr_courts_needed = max_nr_teams // self.mv.settings.min_nr_teams_in_match
        return max(0, len(self.mv.courts) - max_nr_courts_needed)

