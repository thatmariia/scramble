from ortools.sat.python.cp_model import CpModel, IntVar, LinearExpr, Domain
import math
from scramble.core import Level
from scramble.settings import Goal
from scramble.solver.model_variables import ModelVariables
from scramble.solver.objective.function_protocol import ScoringFunction
from scramble.solver.utils import define_and_var, define_or_var, absolute_slack


# --- Individual goal scoring functions ---

def score_keep_ideal_team_size(mdl: CpModel, mv: ModelVariables) -> LinearExpr | IntVar:
    """
    Penalty for teams not having the ideal number of players.
    Higher deviation from the ideal team size = higher penalty.

    Conforms to the ScoreFunction protocol.
    """
    if mv.settings.min_team_size == mv.settings.max_team_size:
        return mdl.new_int_var(0, 0, "ideal_team_size_score")

    ideal_team_size = mv.settings.min_team_size
    terms: list[IntVar] = []
    for team_id in range(mv.nr_teams):
        # calculate the deviation from the ideal team size
        diff = mdl.new_int_var(-mv.settings.max_team_size, mv.settings.max_team_size, f"diff_t{team_id}")
        # abs_diff = mdl.new_int_var(0, len(mv.active_players), f"abs_diff_t{team_id}")

        team_size = sum(mv.player_in_team[player.id, team_id] for player in mv.active_players)
        mdl.add(diff == team_size - ideal_team_size).only_enforce_if(mv.team_active[team_id])
        mdl.add(diff == 0).only_enforce_if(mv.team_active[team_id].Not())
        # mdl.add_abs_equality(abs_diff, diff)
        abs_diff = absolute_slack(mdl, diff, f"abs_diff_t{team_id}", mv.settings.max_team_size)

        terms.append(abs_diff)
    return sum(terms)


def score_balance_lvl(mdl: CpModel, mv: ModelVariables) -> LinearExpr | IntVar:
    """
    Penalty for unbalanced teams in terms of player level on the same court.
    Higher pairwise level difference = higher penalty.

    Conforms to the ScoreFunction protocol.
    """
    terms: list[IntVar] = []

    max_lvl = max(p.level.value for p in mv.active_players)
    max_total = max_lvl * mv.settings.max_team_size
    team_sizes = list(range(mv.settings.min_team_size, mv.settings.max_team_size + 1))
    lcm_sizes = math.lcm(*team_sizes)
    size_scales = {size: lcm_sizes // size for size in team_sizes}

    total_lvl: dict[int, IntVar] = {}
    team_size: dict[int, IntVar] = {}
    scaled_avg: dict[int, IntVar] = {}
    for team_id in range(mv.nr_teams):
        team_size[team_id] = mdl.new_int_var(0, mv.settings.max_team_size, f"team_size_t{team_id}")
        mdl.add(
            team_size[team_id] == sum(
                mv.player_in_team[(player.id, team_id)]
                for player in mv.active_players
            )
        )

        total_lvl[team_id] = mdl.new_int_var(0, max_total, f"total_lvl_t{team_id}")
        mdl.add(
            total_lvl[team_id] == sum(
                player.level * mv.player_in_team[(player.id, team_id)]
                for player in mv.active_players
            )
        )

        table = []
        for size in team_sizes:
            scaled_lvl = mdl.new_int_var(0, size_scales[size] * max_lvl * mv.settings.max_team_size, f"tot_scaled_t{team_id}_k{size}")
            mdl.add(scaled_lvl == size_scales[size] * total_lvl[team_id])
            table.append(scaled_lvl)

        idx = mdl.new_int_var(0, len(team_sizes) - 1, f"idx_t{team_id}")
        mdl.add(idx == team_size[team_id] - team_sizes[0])
        scaled_avg[team_id] = mdl.new_int_var(0, lcm_sizes * max_total, f"scaled_avg_t{team_id}")
        mdl.add_element(idx, table, scaled_avg[team_id])

    if not mv.court_of_team:
        mv.map_teams_to_courts(mdl)

    for team1_id in range(mv.nr_teams):
        for team2_id in range(team1_id + 1, mv.nr_teams):
            same_court = mdl.new_bool_var(f"same_court_{team1_id}_{team2_id}")
            mdl.add(mv.court_of_team[team1_id] == mv.court_of_team[team2_id]).only_enforce_if(same_court)
            mdl.add(mv.court_of_team[team1_id] != mv.court_of_team[team2_id]).only_enforce_if(same_court.Not())

            both_on_court_and_active = define_and_var(
                mdl,
                f"both_on_court_active_t{team1_id}_t{team2_id}",
                [
                    same_court,
                    mv.team_active[team1_id],
                    mv.team_active[team2_id],
                ],
            )

            bound = lcm_sizes * max_lvl * mv.settings.max_team_size
            gap = mdl.new_int_var(-bound, bound, f"gap_t{team1_id}_t{team2_id}")
            mdl.add(gap == scaled_avg[team1_id] - scaled_avg[team2_id]).only_enforce_if(both_on_court_and_active)
            mdl.add(gap == 0).only_enforce_if(both_on_court_and_active.Not())
            abs_gap = absolute_slack(mdl, gap, f"abs_gap_t{team1_id}_t{team2_id}", lcm_sizes * max_lvl)

            terms.append(abs_gap)

    return sum(terms)


def score_reduce_lvl_gap(mdl: CpModel, mv: ModelVariables) -> LinearExpr | IntVar:
    """
    Penalty for players in the same team having a large level difference.
    Higher absolute level difference = higher penalty.

    Conforms to the ScoreFunction protocol.
    """
    terms: list[IntVar] = []

    if not mv.players_same_team:
        mv.players_in_same_team(mdl)

    if not mv.team_of_player:
        mv.map_players_to_teams(mdl)

    for player_i_id, player_j_id in mv.history.partner_tuples:
        if (player_i_id, player_j_id) not in mv.players_same_team:
            continue

        same_team = mv.players_same_team[(player_i_id, player_j_id)]

        lvl_diff = mdl.new_int_var(-Level.max_value(), Level.max_value(), f"lvl_diff_{player_i_id}_{player_j_id}")
        lvl_i = mv.id_to_player[player_i_id].level.value
        lvl_j = mv.id_to_player[player_j_id].level.value
        mdl.add(lvl_diff == lvl_i - lvl_j).only_enforce_if(same_team)
        mdl.add(lvl_diff == 0).only_enforce_if(same_team.Not())

        # abs_lvl_diff = mdl.new_int_var(0, Level.max_value(), f"abs_lvl_diff_{player_i_id}_{player_j_id}")
        # mdl.add_abs_equality(abs_lvl_diff, lvl_diff)
        abs_lvl_diff = absolute_slack(mdl, lvl_diff, f"abs_lvl_diff_{player_i_id}_{player_j_id}", Level.max_value())

        terms.append(abs_lvl_diff)

    return sum(terms)


def score_diversify_partners(mdl: CpModel, mv: ModelVariables) -> LinearExpr | IntVar:
    """
    Penalty for players playing with the same partner too often.
    Higher frequency of the same partner = higher penalty.

    Conforms to the ScoreFunction protocol.
    """
    terms: list[IntVar] = []

    if not mv.players_same_team:
        mv.players_in_same_team(mdl)

    if not mv.team_of_player:
        mv.map_players_to_teams(mdl)

    for player_i_id, player_j_id in mv.history.partner_tuples:
        if (player_i_id, player_j_id) not in mv.players_same_team:
            continue

        freq = mv.history.get_partner_frequency(player_i_id, player_j_id)
        same_team = mv.players_same_team[(player_i_id, player_j_id)]
        terms.append(same_team * freq)
    return sum(terms)


def score_diversify_opponents(mdl: CpModel, mv: ModelVariables) -> LinearExpr | IntVar:
    """
    Penalty for players playing against the same opponent too often.
    Higher frequency of the same opponent = higher penalty.

    Conforms to the ScoreFunction protocol.
    """
    terms: list[IntVar] = []

    if not mv.players_same_court_diff_teams:
        mv.players_in_same_court_diff_teams(mdl)

    for player_i_id, player_j_id in mv.history.opponent_tuples:
        if (player_i_id, player_j_id) not in mv.players_same_court_diff_teams:
            continue

        freq = mv.history.get_opponent_frequency(player_i_id, player_j_id)
        valid_pair = mv.players_same_court_diff_teams[(player_i_id, player_j_id)]
        terms.append(valid_pair * freq)

    return sum(terms)


def score_maximize_courts_usage(mdl: CpModel, mv: ModelVariables) -> LinearExpr | IntVar:
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
        total_teams = mdl.new_int_var(0, mv.nr_teams, f"total_teams_on_{court.id}")
        mdl.add(total_teams == sum(teams_on_court))

        # penalty = teams on court - min required (if positive)
        overload = mdl.new_int_var(0, mv.nr_teams, f"overload_{court.id}")
        mdl.add(overload == total_teams - min_teams).only_enforce_if(mv.court_active[court.id])
        mdl.add(overload == 0).only_enforce_if(mv.court_active[court.id].Not())

        terms.append(overload)

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
