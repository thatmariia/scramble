from ortools.sat.python.cp_model import CpModel, IntVar, LinearExpr
from scramble.solver.model_variables import ModelVariables
from scramble.solver.objective.function_protocol import ScoringFunction
from scramble.settings import Goal
from scramble.solver.utils import define_and_var, define_or_var


# --- Individual goal scoring functions ---

def score_keep_ideal_team_size(mdl: CpModel, mv: ModelVariables) -> LinearExpr | IntVar:
    """
    Penalty for teams not having the ideal number of players.
    Higher deviation from the ideal team size = higher penalty.

    Conforms to the ScoreFunction protocol.
    """
    ideal_team_size = mv.settings.min_team_size
    terms: list[IntVar] = []
    for team_id in range(mv.nr_teams):
        # calculate team size of the current team
        team_size = mdl.new_int_var(0, len(mv.active_players), f"size_t{team_id}")
        mdl.add(team_size == sum(mv.player_in_team[player.id, team_id] for player in mv.active_players))

        # calculate the deviation from the ideal team size
        dev = mdl.new_int_var(0, len(mv.active_players), f"dev_t{team_id}")
        mdl.add_abs_equality(dev, team_size - ideal_team_size)

        # multiply by the team active variable to only count if the team is active
        dev_if_used = mdl.new_int_var(0, len(mv.active_players), f"dev_used_t{team_id}")
        mdl.add_multiplication_equality(dev_if_used, [dev, mv.team_active[team_id]])

        terms.append(dev_if_used)
    return sum(terms)


def score_balance_lvl(mdl: CpModel, mv: ModelVariables) -> LinearExpr | IntVar:
    """
    Penalty for unbalanced teams in terms of player level on the same court.
    Higher pairwise level difference = higher penalty.

    Conforms to the ScoreFunction protocol.
    """
    max_lvl = max(p.level.value for p in mv.active_players)
    max_total = max_lvl * len(mv.active_players)
    max_players = len(mv.active_players)

    # pre-compute each team's total level
    total_lvl: dict[int, IntVar] = {}
    team_size: dict[int, IntVar] = {}
    for team_id in range(mv.nr_teams):
        team_size[team_id] = mdl.new_int_var(0, max_players, f"team_size_t{team_id}")
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

    # build pairwise imbalance only when teams share a court
    terms: list[IntVar] = []
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

                left = mdl.new_int_var(0, max_total * max_players, f"left_t{team1_id}_t{team2_id}_c{court.id}")
                right = mdl.new_int_var(0, max_total * max_players, f"right_t{team1_id}_t{team2_id}_c{court.id}")

                mdl.add_multiplication_equality(left, [total_lvl[team1_id], team_size[team2_id]])
                mdl.add_multiplication_equality(right, [total_lvl[team2_id], team_size[team1_id]])

                diff = mdl.new_int_var(0, max_total * max_players, f"avg_diff_t{team1_id}_t{team2_id}_c{court.id}")
                mdl.add_abs_equality(diff, left - right)

                diff_if_used = mdl.new_int_var(0, max_total * max_players, f"avg_diff_used_t{team1_id}_t{team2_id}_c{court.id}")
                mdl.add_multiplication_equality(diff_if_used, [diff, both_on_court])

                terms.append(diff_if_used)
    return sum(terms)


def score_diversify_partners(mdl: CpModel, mv: ModelVariables) -> LinearExpr | IntVar:
    """
    Penalty for players playing with the same partner too often.
    Higher frequency of the same partner = higher penalty.

    Conforms to the ScoreFunction protocol.
    """
    terms: list[IntVar] = []

    # map players to their teams
    team_of_player: dict[str, IntVar] = {}
    for player in mv.active_players:
        team_var = mdl.new_int_var(0, mv.nr_teams - 1, f"team_of_{player.id}")
        team_of_player[player.id] = team_var
        for team_id in range(mv.nr_teams):
            mdl.add(team_var == team_id).only_enforce_if(mv.player_in_team[(player.id, team_id)])

    for i in range(len(mv.active_players)):
        for j in range(i + 1, len(mv.active_players)):
            player_i = mv.active_players[i]
            player_j = mv.active_players[j]
            freq = mv.history.get_partner_frequency(player_i.id, player_j.id)

            if freq == 0:
                continue  # skip pairs with no penalty

            same_team = mdl.new_bool_var(f"same_team_{player_i.id}_{player_j.id}")

            # same_team is true iff both players are on same team
            mdl.add(team_of_player[player_i.id] == team_of_player[player_j.id]).only_enforce_if(same_team)
            mdl.add(team_of_player[player_i.id] != team_of_player[player_j.id]).only_enforce_if(same_team.Not())

            # penalty = freq * same_team
            penalty_if_used = mdl.new_int_var(0, freq, f"penalty_{player_i.id}_{player_j.id}")
            mdl.add_multiplication_equality(penalty_if_used, [freq, same_team])

            terms.append(penalty_if_used)
    return sum(terms)


def score_diversify_opponents(mdl: CpModel, mv: ModelVariables) -> LinearExpr | IntVar:
    """
    Penalty for players playing against the same opponent too often.
    Higher frequency of the same opponent = higher penalty.

    Conforms to the ScoreFunction protocol.
    """
    terms: list[IntVar] = []

    # map players to their teams and courts
    team_of_player: dict[str, IntVar] = {}
    court_of_player: dict[str, IntVar] = {}
    for player in mv.active_players:
        team_var = mdl.new_int_var(0, mv.nr_teams - 1, f"team_of_{player.id}")
        team_of_player[player.id] = team_var
        for team_id in range(mv.nr_teams):
            mdl.add(team_var == team_id).only_enforce_if(mv.player_in_team[(player.id, team_id)])

        court_ids = [court.id for court in mv.courts]
        team_to_court_index = []

        for team_id in range(mv.nr_teams):
            # figure out which court each team is on
            court_index_for_team = mdl.new_int_var(0, len(court_ids) - 1, f"court_index_for_team_{team_id}")
            court_bools = [mv.team_on_court[(team_id, cid)] for cid in court_ids]
            mdl.add_element(court_index_for_team, court_bools, 1)
            team_to_court_index.append(court_index_for_team)

        # player’s court is determined by their team's assigned court index
        court_var = mdl.new_int_var(0, len(court_ids) - 1, f"court_of_{player.id}")
        court_of_player[player.id] = court_var
        mdl.add_element(team_of_player[player.id], team_to_court_index, court_var)

    for i in range(len(mv.active_players)):
        for j in range(i + 1, len(mv.active_players)):
            player_i = mv.active_players[i]
            player_j = mv.active_players[j]
            freq = mv.history.get_opponent_frequency(player_i.id, player_j.id)

            if freq == 0:
                continue  # skip pairs with no penalty

            same_court = mdl.new_bool_var(f"same_court_{player_i.id}_{player_j.id}")

            # same_court is true iff both players are on the same court
            mdl.add(court_of_player[player_i.id] == court_of_player[player_j.id]).only_enforce_if(same_court)
            mdl.add(court_of_player[player_i.id] != court_of_player[player_j.id]).only_enforce_if(same_court.Not())

            different_team = mdl.new_bool_var(f"different_team_{player_i.id}_{player_j.id}")

            # different_team is true iff both players are on different teams
            mdl.add(team_of_player[player_i.id] != team_of_player[player_j.id]).only_enforce_if(different_team)
            mdl.add(team_of_player[player_i.id] == team_of_player[player_j.id]).only_enforce_if(different_team.Not())

            valid_pair = define_and_var(
                mdl,
                f"valid_pair_{player_i.id}_{player_j.id}",
                [same_court, different_team]
            )

            penalty_if_used = mdl.new_int_var(0, freq, f"penalty_{player_i.id}_{player_j.id}")
            mdl.add_multiplication_equality(penalty_if_used, [freq, valid_pair])
            terms.append(penalty_if_used)
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
