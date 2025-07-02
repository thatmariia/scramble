from ortools.sat.python.cp_model import CpModel
from scramble.solver.model_variables import ModelVariables


def add_hints(mdl: CpModel, mv: ModelVariables):
    """
    Adds hints to the model.
    This helps guide the solver towards more optimal solutions.
    """
    players = sorted(mv.active_players, key=lambda p: p.level.value, reverse=True)

    nr_teams = mv.nr_teams
    nr_courts = len(mv.courts)
    min_team_size = mv.settings.min_team_size
    min_teams_in_match = mv.settings.min_nr_teams_in_match

    # assign players to teams, respecting min_team_size
    player_in_team = {}
    team_ids_with_players = []
    player_idx = 0
    last_repeated_team_id = 0
    i = 0
    while player_idx < len(players):
        team_id = i % nr_teams
        i += 1
        if (len(players) - player_idx) < min_team_size:
            team_id = last_repeated_team_id
            last_repeated_team_id += 1
            last_repeated_team_id %= nr_teams
        for in_team_idx in range(min_team_size):
            if player_idx < len(players):
                player = players[player_idx]
                player_in_team[(player.id, team_id)] = 1
                if team_id not in team_ids_with_players:
                    team_ids_with_players.append(team_id)
                player_idx += 1

    # assign teams to courts, respecting min_teams_in_match
    team_on_court = {}
    court_ids_with_teams = []
    team_idx = 0
    last_repeated_court_idx = 0
    i = 0
    while team_idx < len(team_ids_with_players):
        court_idx = i % nr_courts
        i += 1
        if (len(team_ids_with_players) - team_idx) < min_teams_in_match:
            court_idx = last_repeated_court_idx
            last_repeated_court_idx += 1
            last_repeated_court_idx %= nr_courts
        for in_court_idx in range(min_teams_in_match):
            if team_idx < len(team_ids_with_players):
                team_id = team_ids_with_players[team_idx]
                used_court = mv.courts[court_idx]
                team_on_court[(team_id, used_court.id)] = 1
                if used_court.id not in court_ids_with_teams:
                    court_ids_with_teams.append(used_court.id)
                team_idx += 1

    team_ids_with_players = set(team_ids_with_players)
    court_ids_with_teams = set(court_ids_with_teams)

    for team_id in range(mv.nr_teams):
        mdl.add_hint(mv.team_active[team_id], 1 if team_id in team_ids_with_players else 0)

        for player in mv.active_players:
            if (player.id, team_id) in player_in_team:
                mdl.add_hint(mv.player_in_team[(player.id, team_id)], player_in_team[(player.id, team_id)])

        for court in mv.courts:
            if (team_id, court.id) in team_on_court:
                mdl.add_hint(mv.team_on_court[(team_id, court.id)], team_on_court[(team_id, court.id)])

    for court in mv.courts:
        mdl.add_hint(mv.court_active[court.id], 1 if court.id in court_ids_with_teams else 0)
