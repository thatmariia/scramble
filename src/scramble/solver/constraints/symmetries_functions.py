from ortools.sat.python.cp_model import CpModel, IntVar
from scramble.solver.model_variables import ModelVariables
from scramble.solver.constraints.function_protocol import ConstraintFunction

from typing import Callable, Hashable


def _add_symmetry_breaking_min_index_ordering(
    mdl: CpModel,
    entity_ids: list[Hashable],
    group_ids: list[Hashable],
    is_entity_in_group: Callable[[Hashable, Hashable], IntVar],
    is_group_active: Callable[[Hashable], IntVar],
    prefix: str
):
    """
    Generic symmetry-breaking: Enforce increasing minimum index of entities assigned to groups,
    conditioned on both groups being active.

    Parameters
    ----------
    entity_ids : list[Hashable]
        List of ordered entity identifiers (e.g., players or teams).
    group_ids : list[Hashable]
        List of ordered group identifiers (e.g., teams or courts).
    is_entity_in_group : (entity_id, group_id) -> BoolVar
        Function returning BoolVar indicating if entity is in group.
    is_group_active : group_id -> BoolVar
        Function returning BoolVar indicating if group is active.
    prefix : str
        Prefix for variable names.
    """
    big_m = len(entity_ids)
    min_idx = {}

    for group_id in group_ids:
        masked = []
        for idx, entity_id in enumerate(entity_ids):
            in_group = is_entity_in_group(entity_id, group_id)
            masked_idx = mdl.new_int_var(0, big_m, f"{prefix}_masked_idx_{idx}_{group_id}")
            mdl.add(masked_idx >= idx)
            mdl.add(masked_idx <= idx + big_m * (1 - in_group))
            masked.append(masked_idx)

        min_idx[group_id] = mdl.new_int_var(0, big_m, f"{prefix}_min_idx_{group_id}")
        mdl.add_min_equality(min_idx[group_id], masked)

    for i in range(len(group_ids) - 1):
        g1, g2 = group_ids[i], group_ids[i + 1]
        both_active = mdl.new_bool_var(f"{prefix}_both_active_{g1}_{g2}")
        mdl.add_bool_and([is_group_active(g1), is_group_active(g2)]).only_enforce_if(both_active)

        mdl.add(
            min_idx[g1] + big_m * (1 - both_active) <
            min_idx[g2] + big_m * (1 - both_active)
        ).only_enforce_if(both_active)


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

    _add_symmetry_breaking_min_index_ordering(
        mdl=mdl,
        entity_ids=[p.id for p in mv.active_players],
        group_ids=list(range(mv.nr_teams)),
        is_entity_in_group=lambda pid, tid: mv.player_in_team[(pid, tid)],
        is_group_active=lambda tid: mv.team_active[tid],
        prefix="symm_team"
    )


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

    sorted_courts = sorted(mv.courts, key=lambda c: c.id)
    _add_symmetry_breaking_min_index_ordering(
        mdl=mdl,
        entity_ids=list(range(mv.nr_teams)),
        group_ids=[c.id for c in sorted_courts],
        is_entity_in_group=lambda tid, cid: mv.team_on_court[(tid, cid)],
        is_group_active=lambda cid: mv.court_active[cid],
        prefix="symm_court"
    )


def symmetry_anchor_first_player(mdl: CpModel, mv: ModelVariables):
    """
    Anchors the first player (player 0) to be in team 0.
    This is a specific symmetry-breaking constraint that ensures player 0 is always assigned to team 0.

    Conforms to the ConstraintFunction protocol.
    """
    if mv.active_players and mv.nr_teams > 0:
        p0 = mv.active_players[0].id
        mdl.add(mv.team_active[0] == 1)
        mdl.add(mv.player_in_team[(p0, 0)] == 1)


def symmetry_anchor_first_team(mdl: CpModel, mv: ModelVariables):
    """
    Anchors the first team (team 0) to be on the first court (court 0).
    This is a specific symmetry-breaking constraint that ensures team 0 is always assigned to court 0.

    Conforms to the ConstraintFunction protocol.
    """
    if mv.courts and mv.nr_teams > 0:
        c0 = mv.courts[0].id
        mdl.add(mv.court_active[c0] == 1)
        mdl.add(mv.team_on_court[(0, c0)] == 1)


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
    symmetry_anchor_first_player,
    symmetry_anchor_first_team,
    symmetry_team_groups,
    symmetry_court_groups
]

