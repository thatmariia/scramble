import pytest
import logging
from scramble.core import Level, Court, Player, Round, HistoryManager
from scramble.solver import ScrambleSolver
from scramble.settings import Settings

def get_players(num_players: int, level: Level, start_idx=1):
    players = []
    for i in range(start_idx - 1, start_idx - 1 + num_players):
        name = f"Player {i+1}"
        player = Player(name, level, f"{i+1}", f"{i+1}")
        players.append(player)
    return players

def get_courts(num_courts: int):
    courts = []
    for i in range(num_courts):
        name = f"Court {i+1}"
        court = Court(name, id=f"{i+1}")
        courts.append(court)
    return courts

def get_solver(num_players: int, num_courts: int):
    players = get_players(num_players, Level.BEGINNER)
    courts = get_courts(num_courts)

    history = HistoryManager()
    settings = Settings()
    solver = ScrambleSolver(players, history, courts, settings)
    return solver

def round_to_tuples(round: Round) -> frozenset[frozenset[frozenset[str]]]:
    result = set()
    for match in round.matches:
        match_result = set()
        for team in match.teams:
            ids = frozenset(team.player_ids())
            match_result.add(ids)
        result.add(frozenset(match_result))
    return frozenset(result)

@pytest.mark.parametrize("num_matches", [
    pytest.param(1),
    pytest.param(2),
    # pytest.param(15),
])
@pytest.mark.timeout(60)
def test_n_matches_no_history_same_level(num_matches, caplog):
    caplog.set_level(logging.DEBUG)
    solver = get_solver(num_players=num_matches * 4, num_courts=num_matches)
    round = solver.solve()

    assert len(round.matches) == num_matches

    for i in range(num_matches):
        assert len(round.matches[i].all_player_ids()) == 4
        assert len(round.matches[i].teams) == 2

def test_1_match_same_level(caplog):
    caplog.set_level(logging.DEBUG)
    history = HistoryManager()

    rounds = []
    for _ in range(5):
        solver = get_solver(num_players=4, num_courts=1)
        solver.history = history
        round = solver.solve()
        rounds.append(round_to_tuples(round))
        history.update_from_round(round)

        assert len(round.matches) == 1
        assert len(round.matches[0].all_player_ids()) == 4
        assert len(round.matches[0].teams) == 2

    expected_unique = 3
    assert len(set(rounds)) == expected_unique
    assert rounds[-1] in rounds[:expected_unique]

def test_1_match_qktoc_same_level(caplog):
    caplog.set_level(logging.DEBUG)
    history = HistoryManager()

    rounds = []
    for _ in range(6):
        solver = get_solver(num_players=6, num_courts=1)
        solver.history = history
        round = solver.solve()
        rounds.append(round_to_tuples(round))
        history.update_from_round(round)

        assert len(round.matches) == 1
        assert len(round.matches[0].all_player_ids()) == 6
        assert len(round.matches[0].teams) == 3

    expected_unique = [5, 6]
    assert len(set(rounds)) in expected_unique

def test_2_matches_different_levels(caplog):
    players_beginner = get_players(4, Level.BEGINNER, 1)
    players_intermediate = get_players(4, Level.INTERMEDIATE, 5)

    players = []
    players.extend(players_beginner)
    players.extend(players_intermediate)
    courts = get_courts(2)

    history = HistoryManager()
    settings = Settings()
    solver = ScrambleSolver(players, history, courts, settings)
    round = solver.solve()

    assert len(round.matches) == 2
    for round in round.matches:
        players = [player for team in round.teams for player in team.players]
        levels = set(player.level for player in players)
        assert len(levels) == 1

@pytest.mark.timeout(60)
def test_1_team_qkotc_1_team_match():
    solver = get_solver(num_players=10, num_courts=2)
    round = solver.solve()

    assert len(round.matches) == 2
