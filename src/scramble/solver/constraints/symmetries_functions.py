from ortools.sat.python.cp_model import CpModel
from scramble.solver.model_variables import ModelVariables
from scramble.solver.constraints.function_protocol import ConstraintFunction


# --- Individual constraint functions ---

def symmetry_teams(mdl: CpModel, mv: ModelVariables):
    """
    Adds symmetry-breaking constraints over teams to reduce redundant team labelings.
    Reduces equivalent solutions caused by permutation of team IDs.
    - Defines a "minimum player index" per team (based on player ordering).
    - Forces that these minima are strictly increasing across active teams.
    - Also forces the player with the absolute lowest index to be assigned to team 0.

    Conforms to the ConstraintFunction protocol.
    """
    if not mv.active_players:
        return

    player_id_to_index = {player.id: i for i, player in enumerate(mv.active_players)}
    max_player_index = len(mv.active_players) - 1
    big_m = max_player_index + 1

    min_id = {}

    for team_id in range(mv.nr_teams):
        # create masked player indices for this team
        idx_vars = []
        for player in mv.active_players:
            idx = player_id_to_index[player.id]
            const_idx = mdl.new_int_var(idx, idx, f"idx_{idx}_t{team_id}")
            masked_idx = mdl.new_int_var(0, big_m, f"masked_idx_{idx}_t{team_id}")
            var = mv.player_in_team[(player.id, team_id)]
            mdl.add(masked_idx == const_idx).only_enforce_if(var)
            mdl.add(masked_idx == big_m).only_enforce_if(var.Not())
            idx_vars.append(masked_idx)

        # define min index variable for this team
        min_var = mdl.new_int_var(0, big_m, f"min_idx_t{team_id}")
        mdl.add_min_equality(min_var, idx_vars)
        min_id[team_id] = min_var

    # enforce increasing minimum player index across active teams
    for t in range(mv.nr_teams - 1):
        both_active = mdl.new_bool_var(f"both_teams_active_{t}_{t+1}")
        mdl.add_bool_and([mv.team_active[t], mv.team_active[t + 1]]).only_enforce_if(both_active)
        mdl.add(min_id[t] < min_id[t + 1]).only_enforce_if(both_active)


def symmetry_courts(mdl: CpModel, mv: ModelVariables):
    """
    Adds symmetry-breaking constraints over courts to reduce redundant permutations.
    Reduces equivalent solutions caused by permutation of court IDs.
    - Defines a "minimum team index" for each court (based on team ordering).
    - Forces that these minima are strictly increasing across active courts.
    - Optionally anchors team 0 to be on court 0.

    Conforms to the ConstraintFunction protocol.
    """
    if not mv.courts or mv.nr_teams == 0:
        return

    court_id_to_index = {court.id: i for i, court in enumerate(mv.courts)}
    max_team_index = mv.nr_teams - 1
    big_m = max_team_index + 1

    min_team_on_court = {}

    for court in mv.courts:
        # create masked team indices for this court
        idx_vars = []
        for team_id in range(mv.nr_teams):
            const_idx = mdl.new_int_var(team_id, team_id, f"team_idx_{team_id}_c{court.id}")
            masked_idx = mdl.new_int_var(0, big_m, f"masked_idx_{team_id}_c{court.id}")
            var = mv.team_on_court[(team_id, court.id)]
            mdl.add(masked_idx == const_idx).only_enforce_if(var)
            mdl.add(masked_idx == big_m).only_enforce_if(var.Not())
            idx_vars.append(masked_idx)

        # define min team index variable for this court
        min_var = mdl.new_int_var(0, big_m, f"min_team_idx_c{court.id}")
        mdl.add_min_equality(min_var, idx_vars)
        min_team_on_court[court.id] = min_var

    # enforce increasing minimum team index across active courts
    sorted_court_ids = sorted(court_id_to_index, key=lambda cid: court_id_to_index[cid])
    for i in range(len(sorted_court_ids) - 1):
        c1 = sorted_court_ids[i]
        c2 = sorted_court_ids[i + 1]
        both_active = mdl.new_bool_var(f"both_courts_active_{c1}_{c2}")
        mdl.add_bool_and([mv.court_active[c1], mv.court_active[c2]]).only_enforce_if(both_active)
        mdl.add(min_team_on_court[c1] < min_team_on_court[c2]).only_enforce_if(both_active)


def symmetry_anchor_first_player(mdl: CpModel, mv: ModelVariables):
    """
    Anchors the first player (player 0) to be in team 0.
    This is a specific symmetry-breaking constraint that ensures player 0 is always assigned to team 0.

    Conforms to the ConstraintFunction protocol.
    """
    if mv.active_players and mv.nr_teams > 0:
        mdl.add(mv.player_in_team[(mv.active_players[0].id, 0)] == 1).only_enforce_if(mv.team_active[0])


def symmetry_anchor_first_team(mdl: CpModel, mv: ModelVariables):
    """
    Anchors the first team (team 0) to be on the first court (court 0).
    This is a specific symmetry-breaking constraint that ensures team 0 is always assigned to court 0.

    Conforms to the ConstraintFunction protocol.
    """
    if mv.courts and mv.nr_teams > 0:
        mdl.add(mv.team_on_court[(0, mv.courts[0].id)] == 1).only_enforce_if(mv.court_active[mv.courts[0].id])


def symmetry_team_groups(mdl: CpModel, mv: ModelVariables):
    """
    Adds symmetry-breaking constraints to ensure teams are ordered by activity.
    This prevents equivalent solutions caused by reordering of team IDs.

    Conforms to the ConstraintFunction protocol.
    """
    for t in range(mv.nr_teams - 1):
        mdl.add(mv.team_active[t] >= mv.team_active[t + 1])


def symmetry_court_groups(mdl: CpModel, mv: ModelVariables):
    """
    Adds symmetry-breaking constraints to ensure courts are ordered by activity.
    This prevents equivalent solutions caused by reordering of court IDs.

    Conforms to the ConstraintFunction protocol.
    """
    sorted_courts = sorted(mv.courts, key=lambda c: c.id)  # assuming string IDs
    for i in range(len(sorted_courts) - 1):
        c1, c2 = sorted_courts[i], sorted_courts[i + 1]
        mdl.add(mv.court_active[c1.id] >= mv.court_active[c2.id])


# --- Symmetry-breaking function registry ---

SYMMETRY_FUNCTIONS: list[ConstraintFunction] = [
    symmetry_teams,
    symmetry_courts,
    # symmetry_anchor_first_player,
    # symmetry_anchor_first_team,
    symmetry_team_groups,
    symmetry_court_groups
]

