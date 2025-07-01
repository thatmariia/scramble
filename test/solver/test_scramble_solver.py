import pytest
import logging
from scramble.core import Level, Court, Player, Round, HistoryManager
from scramble.solver import ScrambleSolver
from scramble.settings import Settings


def get_solver(num_players: int, num_courts: int):
    players = []
    for i in range(num_players):
        name = f"Player {i+1}"
        player = Player(name, Level.BEGINNER, f"{i+1}", f"{i+1}")
        players.append(player)

    courts = []
    for i in range(num_courts):
        name = f"Court {i+1}"
        court = Court(name, id=f"{i+1}")
        courts.append(court)

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
    pytest.param(15),
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

    assert len(set(rounds)) == 3
    assert rounds[3] in rounds[:3]

@pytest.mark.timeout(60)
def test_1_team_qkotc_1_team_match():
    solver = get_solver(num_players=10, num_courts=2)
    round = solver.solve()

    assert len(round.matches) == 2
