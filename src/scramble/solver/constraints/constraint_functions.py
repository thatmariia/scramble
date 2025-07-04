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


def constraint_team_size(mdl: CpModel, mv: ModelVariables):
    """
    Ensures that each active team has a size within the defined limits.

    Conforms to the ConstraintFunction protocol.
    """
    for team_id in range(mv.nr_teams):
        team_players = [
            mv.player_in_team[(player.id, team_id)]
            for player in mv.active_players
        ]
        mdl.add(sum(team_players) >= mv.settings.min_team_size).only_enforce_if(mv.team_active[team_id])
        mdl.add(sum(team_players) <= mv.settings.max_team_size).only_enforce_if(mv.team_active[team_id])
        mdl.add(sum(team_players) == 0).only_enforce_if(mv.team_active[team_id].Not())


def constraint_min_nr_teams_on_court(mdl: CpModel, mv: ModelVariables):
    """
    Ensures that each active court has at least the minimum number of teams.

    Conforms to the ConstraintFunction protocol.
    """
    for court in mv.courts:
        teams_on_court = [
            mv.team_on_court[(team_id, court.id)]
            for team_id in range(mv.nr_teams)
        ]
        mdl.add(sum(teams_on_court) >= mv.settings.min_nr_teams_in_match).only_enforce_if(mv.court_active[court.id])
        mdl.add(sum(teams_on_court) == 0).only_enforce_if(mv.court_active[court.id].Not())


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


def constraint_team_active(mdl: CpModel, mv: ModelVariables):
    """
    Ensures that each team is active if it has players.

    Conforms to the ConstraintFunction protocol.
    """
    for team_id in range(mv.nr_teams):
        team_players = [
            mv.player_in_team[(player.id, team_id)]
            for player in mv.active_players
        ]

        size = mdl.new_int_var(0, len(mv.active_players), f"size_t{team_id}")
        mdl.add(size == sum(team_players))

        mdl.add(size >= 1).only_enforce_if(mv.team_active[team_id])
        mdl.add(size == 0).only_enforce_if(mv.team_active[team_id].Not())


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

        mdl.add(sum(team_on_courts) == 1).only_enforce_if(mv.team_active[team_id])
        mdl.add(sum(team_on_courts) == 0).only_enforce_if(mv.team_active[team_id].Not())


def constraint_court_active(mdl: CpModel, mv: ModelVariables):
    """
    Ensures that each court is active if it has teams.

    Conforms to the ConstraintFunction protocol.
    """
    for court in mv.courts:
        teams_on_court = [
            mv.team_on_court[(team_id, court.id)]
            for team_id in range(mv.nr_teams)
        ]

        size = mdl.new_int_var(0, mv.nr_teams, f"size_court_{court.id}")
        mdl.add(size == sum(teams_on_court))

        mdl.add(size >= 1).only_enforce_if(mv.court_active[court.id])
        mdl.add(size == 0).only_enforce_if(mv.court_active[court.id].Not())


# --- Constraint function registry ---

CONSTRAINT_FUNCTIONS: list[ConstraintFunction] = [
    constraint_nr_active_teams,
    constraint_nr_active_courts,
    constraint_team_size,
    constraint_min_nr_teams_on_court,
    constraint_player_mapping,
    constraint_team_active,
    constraint_team_mapping,
    constraint_court_active,
]