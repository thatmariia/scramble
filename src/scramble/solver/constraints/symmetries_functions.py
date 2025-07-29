from ortools.sat.colab.flags import define_bool
from ortools.sat.python import cp_model as cp
from ortools.sat.python.cp_model import IntVar
from scramble.solver.model_variables import ModelVariables
from scramble.solver.constraints.function_protocol import ConstraintFunction
from scramble.core import Level
from scramble.solver.utils import define_and_var, reify_existing_with_fallback, reify_with_fallback, multiply_vars

from typing import Callable, Hashable


# def _add_lex_symmetry_breaking(
#     mdl: cp,
#     group_ids: list,
#     active_var: callable,
#     lex_order: list[str],
#     field_exprs: dict[str, callable],
#     field_ubs: dict[str, int],
# ):
#     for i in range(len(group_ids) - 1):
#         g1, g2 = group_ids[i], group_ids[i + 1]
#         act1, act2 = active_var(g1), active_var(g2)
#
#         # if either is inactive, skip ordering between them
#         both_active = define_and_var(mdl, f"lex_{g1}_{g2}_both_active", [act1, act2])
#
#         # build feature vectors
#         x = [field_exprs[f](g1) for f in lex_order]
#         y = [field_exprs[f](g2) for f in lex_order]
#
#         # build the lex-chain
#         prev_all_eq = None
#         or_clauses = []
#         for j in range(len(lex_order)):
#             # x[:j] == y[:j]  and  x[j] < y[j]
#             eq_prev = None if j == 0 else prev_all_eq
#
#             # x[j] < y[j]
#             lt_j = mdl.new_bool_var(f"lex_{g1}_{g2}_f{j}_lt")
#             mdl.add(x[j] < y[j]).only_enforce_if(lt_j)
#             mdl.add(x[j] >= y[j]).only_enforce_if(lt_j.Not())
#
#             if eq_prev is not None:
#                 case = mdl.new_bool_var(f"lex_{g1}_{g2}_case{j}")
#                 mdl.add_bool_and([eq_prev, lt_j]).only_enforce_if(case)
#                 mdl.add_bool_or([eq_prev.Not(), lt_j.Not()]).only_enforce_if(case.Not())
#                 or_clauses.append(case)
#             else:
#                 or_clauses.append(lt_j)
#
#             # x[j] == y[j] (prefix-equality)
#             eq_j = mdl.new_bool_var(f"lex_{g1}_{g2}_f{j}_eq")
#             mdl.add(x[j] == y[j]).only_enforce_if(eq_j)
#             mdl.add(x[j] != y[j]).only_enforce_if(eq_j.Not())
#
#             if eq_prev is not None:
#                 all_eq = mdl.new_bool_var(f"lex_{g1}_{g2}_prefix_eq{j}")
#                 mdl.add_bool_and([eq_prev, eq_j]).only_enforce_if(all_eq)
#                 mdl.add_bool_or([eq_prev.Not(), eq_j.Not()]).only_enforce_if(all_eq.Not())
#             else:
#                 all_eq = eq_j
#
#             prev_all_eq = all_eq
#
#         # All fields equal ⇒ enforce x[-1] <= y[-1]
#         leq_last = mdl.new_bool_var(f"lex_{g1}_{g2}_leq_last")
#         mdl.add(x[-1] <= y[-1]).only_enforce_if(leq_last)
#         mdl.add(x[-1] > y[-1]).only_enforce_if(leq_last.Not())
#
#         or_clauses.append(prev_all_eq if prev_all_eq is not None else leq_last)
#         or_clauses.append(leq_last)
#
#         # Final: if both active, then some lex-less-or-equal case must be true
#         mdl.add_bool_or(or_clauses).only_enforce_if(both_active)
#         # Also, active ordering (optional but helps)
#         mdl.add(act1 >= act2)

def _add_lex_symmetry_breaking(
    mdl: cp,
    group_ids: list,
    active_var: callable,
    lex_order: list[str],
    field_exprs: dict[str, callable],
    field_ubs: dict[str, int],
):
    # Compute factors for lexicographic ordering
    factors = []
    factor = 1
    for field in reversed(lex_order):
        factors.append(factor)
        factor *= field_ubs[field] + 1
    factors = list(reversed(factors))

    def key(g):
        return sum(field_exprs[f](g) * fac for f, fac in zip(lex_order, factors))

    for i in range(len(group_ids) - 1):
        for j in range(i + 1, len(group_ids)):
            g1, g2 = group_ids[i], group_ids[j]
            mdl.add(active_var(g1) >= active_var(g2))
            mdl.add(key(g1) <= key(g2)).only_enforce_if([active_var(g1), active_var(g2)])


def _get_min_idx(
    mdl: cp,
    entity_ids: list[Hashable],
    group_ids: list[Hashable],
    is_entity_in_group: Callable[[Hashable, Hashable], IntVar],
    prefix: str
):
    big_m = len(entity_ids)
    min_idx = {}

    for group_id in group_ids:
        masked = []
        for idx, entity_id in enumerate(entity_ids):
            in_group = is_entity_in_group(entity_id, group_id)
            masked_idx = reify_with_fallback(
                mdl, idx, big_m, in_group, (idx, big_m), f"{prefix}_masked_idx_{idx}_{group_id}"
            )
            masked.append(masked_idx)

        min_idx[group_id] = mdl.new_int_var(0, big_m, f"{prefix}_min_idx_{group_id}")
        selectors = []
        for i, m_i in enumerate(masked):
            sel = mdl.new_bool_var(f"{prefix}_{group_id}_is_min_{i}")
            selectors.append(sel)
            mdl.add(min_idx[group_id] == m_i).only_enforce_if(sel)
            mdl.add(min_idx[group_id] <= m_i)
        mdl.add_exactly_one(selectors)

    return min_idx


def _get_min_k_indices(
    mdl: cp,
    entity_ids: list[Hashable],
    group_ids: list[Hashable],
    is_entity_in_group: Callable[[Hashable, Hashable], IntVar],
    prefix: str,
    k: int
):
    """
    For each group, finds the indices (in entity_ids order) of the first k assigned entities.
    Returns: {group_id: [min0, min1, ..., min(k-1)]}
    If group has fewer than k assigned, dummy index == len(entity_ids).
    """
    big_m = len(entity_ids)
    indices = {}

    for group_id in group_ids:
        assigned = []
        for idx, entity_id in enumerate(entity_ids):
            assigned.append((idx, is_entity_in_group(entity_id, group_id)))

        min_k = []
        prev_assigned = []
        for j in range(k):
            masked = []
            for idx, assigned_var in assigned:
                # Exclude those already picked in previous steps
                if prev_assigned:
                    already_selected = [mdl.new_bool_var(f"{prefix}_gid{group_id}_eid{idx}_is_prev{p}")
                        for p in prev_assigned]
                    for pidx, sel in enumerate(already_selected):
                        # enforce: assigned_var == 1 AND min_k[pidx] == idx → sel == 1
                        eq_bool = mdl.new_bool_var(f"{prefix}_eq_{group_id}_{pidx}_{idx}")
                        mdl.add(min_k[pidx] == idx).only_enforce_if(eq_bool)
                        mdl.add(min_k[pidx] != idx).only_enforce_if(eq_bool.Not())
                        mdl.add(sel == assigned_var).only_enforce_if(eq_bool)
                        mdl.add(sel == 0).only_enforce_if(eq_bool.Not())
                    not_already = mdl.new_bool_var(f"{prefix}_gid{group_id}_eid{idx}_not_already")
                    mdl.add_bool_and([assigned_var] + [~sel for sel in already_selected]).only_enforce_if(not_already)
                else:
                    not_already = assigned_var
                masked_idx = reify_with_fallback(
                    mdl, idx, big_m, not_already, (idx, big_m), f"{prefix}_masked_idx_{j}_{idx}_{group_id}"
                )
                masked.append(masked_idx)

            # Find min of the masked (for j-th min)
            min_var = mdl.new_int_var(0, big_m, f"{prefix}_min{j}_{group_id}")
            selectors = []
            for i, m_i in enumerate(masked):
                sel = mdl.new_bool_var(f"{prefix}_{group_id}_is_min{j}_{i}")
                selectors.append(sel)
                mdl.add(min_var == m_i).only_enforce_if(sel)
                mdl.add(min_var <= m_i)
            mdl.add_exactly_one(selectors)
            min_k.append(min_var)
            prev_assigned.append(min_var)

        indices[group_id] = min_k
    return indices


def _add_symmetry_breaking_min_index_ordering(
    mdl: cp,
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
    is_entity_in_group: (entity_id, group_id) -> BoolVar
        Function returning BoolVar indicating if entity is in group.
    is_group_active : group_id -> BoolVar
        Function returning BoolVar indicating if group is active.
    prefix : str
        Prefix for variable names.
    """
    min_idx = _get_min_idx(
        mdl=mdl,
        entity_ids=entity_ids,
        group_ids=group_ids,
        is_entity_in_group=is_entity_in_group,
        prefix=prefix
    )

    big_m = len(entity_ids)

    for i in range(len(group_ids) - 1):
        g1, g2 = group_ids[i], group_ids[i + 1]
        both_active = define_and_var(mdl, f"{prefix}_both_active_{g1}_{g2}", [is_group_active(g1), is_group_active(g2)])
        mdl.add(
            min_idx[g1] + big_m * (1 - both_active) <
            min_idx[g2] + big_m * (1 - both_active)
        ).only_enforce_if(both_active)


def _add_lex_less_or_equal(mdl, x, y):
    # x, y are lists of IntVar
    # Constrain: x <=_lex y
    n = len(x)
    prev_equal = mdl.new_bool_var('lex_eq_0')
    mdl.add(x[0] <= y[0]).only_enforce_if(prev_equal.Not())
    mdl.add(x[0] == y[0]).only_enforce_if(prev_equal)
    for i in range(1, n):
        curr_equal = mdl.new_bool_var(f'lex_eq_{i}')
        # If all previous equal, then x[i] <= y[i]
        mdl.add(x[i] <= y[i]).only_enforce_if(prev_equal)
        # Chain equalities
        mdl.add(x[i] == y[i]).only_enforce_if(curr_equal)
        mdl.add(x[i] != y[i]).only_enforce_if(curr_equal.Not())
        prev_equal = mdl.new_bool_var(f'lex_eqchain_{i}')
        mdl.add_bool_and([curr_equal, prev_equal]).only_enforce_if(prev_equal)

# --- Individual constraint functions ---


def symmetry_anchor_first(mdl: cp, mv: ModelVariables):
    """
    Anchors the first player (player 0) to be in team 0.
    This is a specific symmetry-breaking constraint that ensures player 0 is always assigned to team 0.

    Conforms to the ConstraintFunction protocol.
    """
    if not mv.active_players or not mv.courts or mv.nr_teams == 0:
        return

    sorted_players = sorted(
        mv.active_players,
        key=lambda p: (p.level.value, p.id)
    )
    sorted_courts = sorted(mv.courts, key=lambda c: c.id)
    p0 = sorted_players[0].id
    c0 = sorted_courts[0].id
    mdl.add(mv.player_in_team[(p0, 0)] == 1)
    mdl.add_implication(
        mv.team_active[0],
        mv.team_on_court[(0, c0)]
    )


def symmetry_team_groups(mdl: cp, mv: ModelVariables):
    if not mv.active_players:
        return

    sorted_players = sorted(mv.active_players, key=lambda p: (p.level.value, p.id))
    min_idx = _get_min_idx(
        mdl=mdl,
        entity_ids=sorted_players,
        group_ids=list(range(mv.nr_teams)),
        is_entity_in_group=lambda pid, tid: mv.player_in_team[(pid.id, tid)],
        prefix="symm_team",
    )
    rank = {p.id: i for i, p in enumerate(sorted_players)}

    lex_order = [
        "min_idx",
        "avg_level",
        "size_deviation",
        "level_range",
        "total_rank",
    ]
    field_ubs = {
        "size_deviation": mv.settings.max_team_size,
        "level_range": Level.max_value() - Level.min_value(),
        "avg_level": mv.settings.lcm_sizes() * Level.max_value(),
        "min_idx": len(mv.active_players) - 1,
        "total_rank": len(mv.active_players) * mv.settings.max_team_size
    }
    field_exprs = {
        "size_deviation": lambda t: mv.settings.max_team_size - mv.team_size[t],
        "level_range": lambda t: mv.team_level_range(mdl, t),
        "avg_level": lambda t: mv.scaled_avg_team_lvl(mdl, t),
        "min_idx": lambda t: min_idx[t],
        "total_rank": lambda t: sum(
            mv.player_in_team[(p.id, t)] * rank[p.id]
            for p in sorted_players
        ),
    }

    _add_lex_symmetry_breaking(
        mdl,
        group_ids=list(range(mv.nr_teams)),
        active_var=lambda t: mv.team_active[t],
        lex_order=lex_order,
        field_exprs=field_exprs,
        field_ubs=field_ubs,
    )


def symmetry_court_groups(mdl: cp, mv: ModelVariables):
    if not mv.courts or mv.nr_teams == 0:
        return

    sorted_courts = sorted(mv.courts, key=lambda c: c.id)
    min_idx = _get_min_idx(
        mdl=mdl,
        entity_ids=list(range(mv.nr_teams)),
        group_ids=[c.id for c in sorted_courts],
        is_entity_in_group=lambda team_id, court_id: mv.team_on_court[(team_id, court_id)],
        prefix="symm_court"
    )
    rank = {c.id: i for i, c in enumerate(sorted_courts)}

    lex_order = [
        "min_idx",
        "nr_teams",
        "court_spread",
        "total_rank"
    ]
    field_ubs = {
        "nr_teams": mv.nr_teams,
        "min_idx": len(sorted_courts) - 1,
        "court_spread": mv.settings.lcm_sizes() * Level.max_value(),
        "total_rank": len(sorted_courts) * mv.nr_teams
    }
    field_exprs = {
        "nr_teams": lambda c: sum(
            mv.team_on_court[(t, c)] for t in range(mv.nr_teams)
        ),
        "min_idx": lambda c: min_idx[c],
        "court_spread": lambda c: mv.court_lvl_spread(mdl, c),
        "total_rank": lambda c: sum(
            mv.team_on_court[(t, c)] * rank[c] for t in range(mv.nr_teams)
        )
    }

    _add_lex_symmetry_breaking(
        mdl,
        group_ids=[c.id for c in sorted_courts],
        active_var=lambda cid: mv.court_active[cid],
        lex_order=lex_order,
        field_exprs=field_exprs,
        field_ubs=field_ubs,
    )



# --- Symmetry-breaking function registry ---

SYMMETRY_FUNCTIONS: list[ConstraintFunction] = [
    symmetry_anchor_first,
    symmetry_team_groups,
    symmetry_court_groups
]

