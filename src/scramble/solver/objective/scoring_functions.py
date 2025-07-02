from ortools.sat.python.cp_model import CpModel, IntVar, LinearExpr
from scramble.core import Level
from scramble.settings import Goal
from scramble.solver.model_variables import ModelVariables
from scramble.solver.objective.function_protocol import ScoringFunction
from scramble.solver.utils import define_and_var, define_or_var
from scramble.solver.objective.utils import map_players_to_teams, map_players_to_courts


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
        dev = mdl.new_int_var(0, len(mv.active_players), f"dev_t{team_id}")
        team_size = sum(mv.player_in_team[player.id, team_id] for player in mv.active_players)
        mdl.add_abs_equality(dev, team_size - ideal_team_size)

        # only count if the team is active
        mdl.add(dev == dev).only_enforce_if(mv.team_active[team_id])
        mdl.add(dev == 0).only_enforce_if(mv.team_active[team_id].Not())

        terms.append(dev)
    return sum(terms)


def score_balance_lvl(mdl: CpModel, mv: ModelVariables) -> LinearExpr | IntVar:
    """
    Penalty for unbalanced teams in terms of player level on the same court.
    Higher pairwise level difference = higher penalty.

    Conforms to the ScoreFunction protocol.
    """
    terms: list[IntVar] = []

    max_lvl = max(p.level.value for p in mv.active_players)
    max_total = max_lvl * len(mv.active_players)

    max_score = Level.max_value() * mv.settings.max_team_size
    team_lvl: dict[int, IntVar] = {}

    for team_id in range(mv.nr_teams):
        # compute team size
        team_size = mdl.new_int_var(mv.settings.min_team_size, mv.settings.max_team_size, f"team_size_t{team_id}")
        mdl.add(
            team_size == sum(mv.player_in_team[(player.id, team_id)] for player in mv.active_players)
        )

        # compute sum of levels in team
        lvl_sum = mdl.new_int_var(0, max_score, f"lvl_sum_t{team_id}")
        mdl.add(
            lvl_sum == sum(
                player.level.value * mv.player_in_team[(player.id, team_id)]
                for player in mv.active_players
            )
        )

        # create score var and link via allowed assignments
        score_var = mdl.new_int_var(0, max_score, f"team_lvl_score_t{team_id}")
        team_lvl[team_id] = score_var

        # allowed mapping: sum, size -> score
        allowed = [
            [lvl_sum_val, team_size_val, score]
            for (lvl_sum_val, team_size_val), score in mv.settings.team_lvl_scores.items()
        ]
        mdl.add_allowed_assignments([lvl_sum, team_size, score_var], allowed)

    # build pairwise imbalance only when teams share a court
    for court in mv.courts:
        for team1_id in range(mv.nr_teams):
            for team2_id in range(team1_id + 1, mv.nr_teams):
                # check if both teams are on the same court
                both_on_court = define_and_var(
                    mdl,
                    f"both_on_court_t{team1_id}_t{team2_id}",
                    [
                        mv.team_on_court[(team1_id, court.id)],
                        mv.team_on_court[(team2_id, court.id)]
                    ]
                )
                diff = mdl.new_int_var(0, max_total, f"avg_diff_t{team1_id}_t{team2_id}_c{court.id}")
                mdl.add_abs_equality(diff, team_lvl[team1_id] - team_lvl[team2_id])

                mdl.add(diff == diff).only_enforce_if(both_on_court)
                mdl.add(diff == 0).only_enforce_if(both_on_court.Not())

                terms.append(diff)
    return sum(terms)


def score_diversify_partners(mdl: CpModel, mv: ModelVariables) -> LinearExpr | IntVar:
    """
    Penalty for players playing with the same partner too often.
    Higher frequency of the same partner = higher penalty.

    Conforms to the ScoreFunction protocol.
    """
    terms: list[IntVar] = []

    if not mv.team_of_player:
        mv.team_of_player = map_players_to_teams(mdl, mv)

    for player_i_id, player_j_id in mv.history.partner_tuples:
        freq = mv.history.get_partner_frequency(player_i_id, player_j_id)

        same_team = mdl.new_bool_var(f"same_team_{player_i_id}_{player_j_id}")

        # same_team is true iff both players are on same team
        mdl.add(mv.team_of_player[player_i_id] == mv.team_of_player[player_j_id]).only_enforce_if(same_team)
        mdl.add(mv.team_of_player[player_i_id] != mv.team_of_player[player_j_id]).only_enforce_if(same_team.Not())

        # penalty
        penalty = mdl.new_int_var(0, freq, f"freq_{player_i_id}_{player_j_id}")
        mdl.add(penalty == freq).only_enforce_if(same_team)
        mdl.add(penalty == 0).only_enforce_if(same_team.Not())

        terms.append(penalty)
    return sum(terms)


def score_diversify_opponents(mdl: CpModel, mv: ModelVariables) -> LinearExpr | IntVar:
    """
    Penalty for players playing against the same opponent too often.
    Higher frequency of the same opponent = higher penalty.

    Conforms to the ScoreFunction protocol.
    """
    terms: list[IntVar] = []

    if not mv.team_of_player:
        mv.team_of_player = map_players_to_teams(mdl, mv)
    if not mv.court_of_player:
        mv.court_of_player = map_players_to_courts(mdl, mv)

    for player_i_id, player_j_id in mv.history.opponent_tuples:
        freq = mv.history.get_opponent_frequency(player_i_id, player_j_id)

        same_court = mdl.new_bool_var(f"same_court_{player_i_id}_{player_j_id}")

        # same_court is true iff both players are on the same court
        mdl.add(mv.court_of_player[player_i_id] == mv.court_of_player[player_j_id]).only_enforce_if(same_court)
        mdl.add(mv.court_of_player[player_i_id] != mv.court_of_player[player_j_id]).only_enforce_if(same_court.Not())

        different_team = mdl.new_bool_var(f"different_team_{player_i_id}_{player_j_id}")

        # different_team is true iff both players are on different teams
        mdl.add(mv.team_of_player[player_i_id] != mv.team_of_player[player_j_id]).only_enforce_if(different_team)
        mdl.add(mv.team_of_player[player_i_id] == mv.team_of_player[player_j_id]).only_enforce_if(different_team.Not())

        valid_pair = define_and_var(
            mdl,
            f"valid_pair_{player_i_id}_{player_j_id}",
            [same_court, different_team]
        )

        # penalty
        penalty = mdl.new_int_var(0, freq, f"freq_{player_i_id}_{player_j_id}")
        mdl.add(penalty == freq).only_enforce_if(valid_pair)
        mdl.add(penalty == 0).only_enforce_if(valid_pair.Not())

        terms.append(penalty)
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
    Goal.DIVERSIFY_PARTNERS: score_diversify_partners,
    Goal.DIVERSIFY_OPPONENTS: score_diversify_opponents,
    Goal.MAXIMIZE_COURTS_USAGE: score_maximize_courts_usage,
}
