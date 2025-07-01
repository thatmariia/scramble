import pytest
import logging
from scramble.core import Level, Court, Player, HistoryManager
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


@pytest.mark.parametrize("num_matches", [
    # pytest.param(1),
    # pytest.param(2),
    # pytest.param(3),
    # pytest.param(4),
    pytest.param(50),
])
# @pytest.mark.timeout(60)
def test_n_matches_no_history_same_level(num_matches, caplog):
    caplog.set_level(logging.DEBUG)
    solver = get_solver(num_players=num_matches * 4, num_courts=num_matches)
    round = solver.solve()

    assert len(round.matches) == num_matches

    for i in range(num_matches):
        assert len(round.matches[i].all_player_ids()) == 4
        assert len(round.matches[i].teams) == 2

    # assert 1 == 2

@pytest.mark.timeout(60)
@pytest.mark.skip(reason="RuntimeError: No feasible solution found")
def test_1_team_qkotc_1_team_match():
    solver = get_solver(num_players=10, num_courts=2)
    round = solver.solve()

    assert len(round.matches) == 2
