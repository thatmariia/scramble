from ortools.sat.python.cp_model import CpModel
import math
from scramble.solver.model_variables import ModelVariables
from scramble.solver.constraints.function_protocol import ConstraintFunction
from scramble.settings import Settings, Goal


# --- Individual constraint functions ---

def constraint_nr_active_teams(mdl: CpModel, mv: ModelVariables):
    """
    Ensures that the number of active teams is within the limits defined by the settings.

    Conforms to the ConstraintFunction protocol.
    """
    if mv.settings.goal_configs[Goal.KEEP_IDEAL_TEAM_SIZE].enabled:
        min_nr_active_teams = len(mv.active_players) // mv.settings.min_team_size
        mdl.add(sum(mv.team_active.values()) >= min_nr_active_teams)

        max_nr_active_teams = math.ceil(len(mv.active_players) / mv.settings.min_team_size)
        mdl.add(sum(mv.team_active.values()) <= max_nr_active_teams)


def constraint_nr_active_courts(mdl: CpModel, mv: ModelVariables):
    """
    Ensures that the number of active courts is within the limits defined by the settings.

    Conforms to the ConstraintFunction protocol.
    """
    if mv.settings.goal_configs[Goal.MAXIMIZE_COURTS_USAGE].enabled:
        min_nr_active_teams = len(mv.active_players) // mv.settings.min_team_size if mv.settings.goal_configs[Goal.KEEP_IDEAL_TEAM_SIZE].enabled else 0
        min_nr_active_courts = min(
            len(mv.courts),
            min_nr_active_teams // mv.settings.min_nr_teams_in_match
        )
        mdl.add(sum(mv.court_active.values()) >= min_nr_active_courts)

        max_nr_active_teams = math.ceil(len(mv.active_players) / mv.settings.min_team_size) if mv.settings.goal_configs[Goal.KEEP_IDEAL_TEAM_SIZE].enabled else mv.nr_teams
        max_nr_active_courts = min(
            len(mv.courts),
            math.ceil(max_nr_active_teams / mv.settings.min_nr_teams_in_match)
        )
        mdl.add(sum(mv.court_active.values()) <= max_nr_active_courts)


def constraint_player_mapping(mdl: CpModel, mv: ModelVariables):
    """
    Ensures that each player is assigned to exactly one team.

    Conforms to the ConstraintFunction protocol.
    """
    for player in mv.active_players:
        teams_with_player = [
            mv.player_in_team[(player.id, team_id)]
            for team_id in range(mv.nr_teams)
        ]
        mdl.add(sum(teams_with_player) == 1)


def constraint_team_active_and_size(mdl: CpModel, mv: ModelVariables):
    """
    Ensures that each team is active if it has players.
    Ensures that each active team has a size within the defined limits.

    Conforms to the ConstraintFunction protocol.
    """
    for team_id in range(mv.nr_teams):
        team_players = [
            mv.player_in_team[(player.id, team_id)]
            for player in mv.active_players
        ]

        mdl.add(mv.team_size[team_id] == sum(team_players))
        is_non_zero = mdl.new_bool_var(f"team_{team_id}_is_non_zero")
        mdl.add(mv.team_size[team_id] >= mv.settings.min_team_size).only_enforce_if(is_non_zero)
        mdl.add(mv.team_size[team_id] <= mv.settings.max_team_size).only_enforce_if(is_non_zero)
        mdl.add(mv.team_size[team_id] == 0).only_enforce_if(is_non_zero.Not())
        mdl.add(mv.team_active[team_id] == is_non_zero)


def constraint_team_mapping(mdl: CpModel, mv: ModelVariables):
    """
    Ensures that each active team is assigned to exactly one court.

    Conforms to the ConstraintFunction protocol.
    """
    for team_id in range(mv.nr_teams):
        team_on_courts = [
            mv.team_on_court[(team_id, court.id)]
            for court in mv.courts
        ]
        mdl.add(sum(team_on_courts) == mv.team_active[team_id])


def constraint_court_active_and_size(mdl: CpModel, mv: ModelVariables):
    """
    Ensures that each court is active if it has teams.
    Ensures that each active court has at least the minimum number of teams.

    Conforms to the ConstraintFunction protocol.
    """
    for court in mv.courts:
        teams_on_court = [
            mv.team_on_court[(team_id, court.id)]
            for team_id in range(mv.nr_teams)
        ]

        is_non_zero = mdl.new_bool_var(f"court_{court.id}_is_non_zero")
        mdl.add(sum(teams_on_court) >= mv.settings.min_nr_teams_in_match).only_enforce_if(is_non_zero)
        mdl.add(sum(teams_on_court) == 0).only_enforce_if(is_non_zero.Not())
        mdl.add(mv.court_active[court.id] == is_non_zero)


# --- Constraint function registry ---

CONSTRAINT_FUNCTIONS: list[ConstraintFunction] = [
    constraint_nr_active_teams,
    constraint_nr_active_courts,
    constraint_player_mapping,
    constraint_team_active_and_size,
    constraint_team_mapping,
    constraint_court_active_and_size,
]