from ortools.sat.python.cp_model import IntVar, LinearExpr, Domain
from ortools.sat.python import cp_model as cp
import math
from itertools import combinations, product
from scramble.core import Level
from scramble.settings import Goal
from scramble.solver.model_variables import ModelVariables
from scramble.solver.objective.function_protocol import ScoringFunction
from scramble.solver.utils import define_and_var, define_or_var, absolute_slack, absolute_value, define_and_var_bool, reify_with_fallback


# --- Individual goal scoring functions ---

def score_keep_ideal_team_size(mdl: cp, mv: ModelVariables) -> LinearExpr | IntVar:
    """
    Penalty for teams not having the ideal number of players.
    Higher deviation from the ideal team size = higher penalty.

    Conforms to the ScoreFunction protocol.
    """
    if mv.settings.min_team_size == mv.settings.max_team_size:
        return mdl.new_int_var(0, 0, "ideal_team_size_score")

    ideal_team_size = mv.settings.min_team_size
    size_range = mv.settings.max_team_size - ideal_team_size
    terms: list[IntVar] = []
    for team_id in range(mv.nr_teams):
        # calculate the deviation from the ideal team size
        diff = mdl.new_int_var(-mv.settings.min_team_size, size_range, f"diff_t{team_id}")
        mdl.add(diff == mv.team_size[team_id] - ideal_team_size)
        abs_diff = absolute_slack(mdl, diff, f"abs_diff_t{team_id}", size_range)
        # abs_diff = absolute_value(mdl, diff, f"abs_diff_t{team_id}", size_range)

        penalty = reify_with_fallback(
            mdl, abs_diff, 0, mv.team_active[team_id],
            (0, size_range), f"penalty_reify_ideal_team_size_t{team_id}"
        )
        terms.append(penalty)
    return sum(terms)


def score_balance_lvl(mdl: cp, mv: ModelVariables) -> LinearExpr | IntVar:
    """
    Penalty for unbalanced teams in terms of player level on the same court.
    Higher pairwise level difference = higher penalty.

    Conforms to the ScoreFunction protocol.
    """
    terms: list[IntVar] = []

    for court in mv.courts:
        terms.append(mv.court_lvl_spread(mdl, court.id))

    return sum(terms)


def score_reduce_lvl_gap(mdl: cp, mv: ModelVariables) -> LinearExpr | IntVar:
    """
    Penalty for players in the same team having a large level difference.
    Higher absolute level difference = higher penalty.

    Conforms to the ScoreFunction protocol.
    """
    terms: list[IntVar] = []

    for team_id in range(mv.nr_teams):
        terms.append(mv.team_level_range(mdl, team_id))

    return sum(terms)


def score_diversify_partners(mdl: cp, mv: ModelVariables) -> LinearExpr | IntVar:
    """
    Penalty for players playing with the same partner too often.
    Higher frequency of the same partner = higher penalty.

    Conforms to the ScoreFunction protocol.
    """
    terms: list[IntVar] = []

    for player_i_id, player_j_id in mv.history.partner_tuples:
        if not mv.player_exists(player_i_id) and not mv.player_exists(player_j_id):
            continue

        freq = mv.history.get_partner_frequency(player_i_id, player_j_id)
        if freq == 0:
            continue

        same_team = mv.players_in_same_team(mdl, player_i_id, player_j_id)

        penalty = reify_with_fallback(
            mdl, freq, 0, same_team,
            (0, freq), f"penalty_reify_partners_{player_i_id}_{player_j_id}"
        )
        terms.append(penalty)
    return sum(terms)


def score_diversify_opponents(mdl: cp, mv: ModelVariables) -> LinearExpr | IntVar:
    """
    Penalty for players playing against the same opponent too often.
    Higher frequency of the same opponent = higher penalty.

    Conforms to the ScoreFunction protocol.
    """
    terms: list[IntVar] = []

    for player_i_id, player_j_id in mv.history.opponent_tuples:
        if not mv.player_exists(player_i_id) and not mv.player_exists(player_j_id):
            continue

        freq = mv.history.get_opponent_frequency(player_i_id, player_j_id)
        if freq == 0:
            continue

        valid_pair = mv.players_in_same_court_diff_team(mdl, player_i_id, player_j_id)

        penalty = reify_with_fallback(
            mdl, freq, 0, valid_pair,
            (0, freq), f"penalty_reify_opponents_{player_i_id}_{player_j_id}"
        )
        terms.append(penalty)

    return sum(terms)


def score_maximize_courts_usage(mdl: cp, mv: ModelVariables) -> LinearExpr | IntVar:
    """
    Penalty for not using all available courts.
    Higher number of unused courts = higher penalty.

    Conforms to the ScoreFunction protocol.
    """
    terms: list[IntVar] = []
    min_teams = mv.settings.min_nr_teams_in_match

    for court in mv.courts:
        teams_on_court = [
            mv.team_on_court[(team_id, court.id)] for team_id in range(mv.nr_teams)
        ]
        overload = mdl.new_int_var(-min_teams, mv.nr_teams, f"overload_{court.id}")
        mdl.add(overload == sum(teams_on_court) - min_teams)

        penalty = reify_with_fallback(
            mdl, overload, 0, mv.court_active[court.id],
            (0, mv.nr_teams), f"penalty_reify_{court.id}"
        )
        terms.append(penalty)

    return sum(terms)


# --- Scoring dispatch map ---

SCORING_FUNCTIONS: dict[Goal, ScoringFunction] = {
    Goal.KEEP_IDEAL_TEAM_SIZE: score_keep_ideal_team_size,
    Goal.BALANCE_LVL: score_balance_lvl,
    Goal.REDUCE_LVL_GAP: score_reduce_lvl_gap,
    Goal.DIVERSIFY_PARTNERS: score_diversify_partners,
    Goal.DIVERSIFY_OPPONENTS: score_diversify_opponents,
    Goal.MAXIMIZE_COURTS_USAGE: score_maximize_courts_usage,
}
