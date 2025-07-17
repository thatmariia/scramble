from ortools.sat.python.cp_model import CpModel
from itertools import chain
from scramble.solver.model_variables import ModelVariables
from scramble.core import Round, Player
from scramble.solver.hints.greedy import greedy_assignment


def add_hints_from_round(mdl: CpModel, mv: ModelVariables, game_round: Round):
    """
    Adds hints to the model based on the provided game round.
    """
    player_in_team = {}
    team_on_court = {}
    team_active = {}
    court_active = {}

    team_id = 0
    for match in game_round.matches:
        for team in match.teams:
            for player in team.players:
                player_in_team[(player.id, team_id)] = 1
            team_on_court[(team_id, match.court.id)] = 1
            team_active[team_id] = 1
            team_id += 1
        court_active[match.court.id] = 1

    for team_id in range(mv.nr_teams):
        mdl.add_hint(mv.team_active[team_id], team_active.get(team_id, 0))

        for player in mv.active_players:
            mdl.add_hint(mv.player_in_team[(player.id, team_id)], player_in_team.get((player.id, team_id), 0))

        for court in mv.courts:
            mdl.add_hint(mv.team_on_court[(team_id, court.id)], team_on_court.get((team_id, court.id), 0))

    for court in mv.courts:
        mdl.add_hint(mv.court_active[court.id], court_active.get(court.id, 0))


def add_startup_hints(mdl: CpModel, mv: ModelVariables):
    """
    Adds hints to the model.
    This helps guide the solver towards more optimal solutions.
    """
    player_in_team, team_on_court, team_active, court_active = greedy_assignment(mv)

    for team_id in range(mv.nr_teams):
        mdl.add_hint(mv.team_active[team_id], team_active.get(team_id, 0))

        for player in mv.active_players:
            mdl.add_hint(mv.player_in_team[(player.id, team_id)], player_in_team.get((player.id, team_id), 0))

        for court in mv.courts:
            mdl.add_hint(mv.team_on_court[(team_id, court.id)], team_on_court.get((team_id, court.id), 0))

    for court in mv.courts:
        mdl.add_hint(mv.court_active[court.id], court_active.get(court.id, 0))
