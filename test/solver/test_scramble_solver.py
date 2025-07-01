import logging
import pytest

from scramble.core import Level, Court, Player, Round, HistoryManager
from scramble.solver import ScrambleSolver
from scramble.settings import Settings


def generate_players(count: int, level: Level, start_index: int = 1) -> list[Player]:
    """Generate a list of players with the given skill level and sequential IDs."""
    return [
        Player(
            name=f"Player {i + 1}",
            level=level,
            id=str(i + 1),
        )
        for i in range(start_index - 1, start_index - 1 + count)
    ]


def generate_courts(count: int) -> list[Court]:
    """Generate a list of court instances with unique IDs."""
    return [Court(name=f"Court {i + 1}", id=str(i + 1)) for i in range(count)]


def create_solver(num_players: int, num_courts: int) -> ScrambleSolver:
    """Create a ScrambleSolver instance with the given number of players and courts."""
    players = generate_players(num_players, Level.BEGINNER)
    courts = generate_courts(num_courts)
    return ScrambleSolver(players, HistoryManager(), courts, Settings())


def round_as_tuple_set(round: Round) -> frozenset[frozenset[frozenset[str]]]:
    """Convert a round into a nested frozenset structure to detect unique match configurations."""
    return frozenset(
        frozenset(
            frozenset(team.player_ids()) for team in match.teams
        )
        for match in round.matches
    )


@pytest.mark.parametrize("num_matches", [1, 2])
@pytest.mark.timeout(60)
def test_rounds_have_expected_structure(num_matches: int, caplog):
    """
    Ensure that each generated round has the correct number of matches and
    that each match consists of 2 teams with 4 players total.
    """
    caplog.set_level(logging.DEBUG)
    solver = create_solver(num_players=num_matches * 4, num_courts=num_matches)
    round = solver.solve()

    assert len(round.matches) == num_matches
    for match in round.matches:
        assert len(match.teams) == 2
        assert len(match.all_player_ids()) == 4


def test_repeated_rounds_yield_limited_variation(caplog):
    """
    Ensure that solving the same scenario repeatedly with shared history yields
    a limited number of unique match configurations.
    """
    caplog.set_level(logging.DEBUG)
    history = HistoryManager()
    unique_rounds = []

    for _ in range(5):
        solver = create_solver(num_players=4, num_courts=1)
        solver.history = history
        round = solver.solve()
        unique_rounds.append(round_as_tuple_set(round))
        history.update_from_round(round)

        assert len(round.matches) == 1
        assert len(round.matches[0].teams) == 2
        assert len(round.matches[0].all_player_ids()) == 4

    expected_variants = 3
    assert len(set(unique_rounds)) == expected_variants
    assert unique_rounds[-1] in unique_rounds[:expected_variants]


def test_3v3_matches_with_history(caplog):
    """
    Test match generation with 6 players, expecting 3v3 matches.
    Validate that a reasonable number of unique configurations are produced.
    """
    caplog.set_level(logging.DEBUG)
    history = HistoryManager()
    unique_rounds = []

    for _ in range(6):
        solver = create_solver(num_players=6, num_courts=1)
        solver.history = history
        round = solver.solve()
        unique_rounds.append(round_as_tuple_set(round))
        history.update_from_round(round)

        assert len(round.matches) == 1
        assert len(round.matches[0].teams) == 3
        assert len(round.matches[0].all_player_ids()) == 6

    assert len(set(unique_rounds)) in [5, 6]


def test_level_based_grouping_on_multiple_courts(caplog):
    """
    Ensure players of different levels are split into separate matches.
    """
    caplog.set_level(logging.DEBUG)
    players = generate_players(4, Level.BEGINNER, start_index=1) + \
              generate_players(4, Level.INTERMEDIATE, start_index=5)
    courts = generate_courts(2)

    solver = ScrambleSolver(players, HistoryManager(), courts, Settings())
    round = solver.solve()

    assert len(round.matches) == 2
    for match in round.matches:
        match_levels = {player.level for team in match.teams for player in team.players}
        assert len(match_levels) == 1  # All players in a match must have the same level


@pytest.mark.timeout(60)
def test_combined_team_and_match_distribution():
    """
    Test with 10 players and 2 courts, expecting 2 matches with correct distribution.
    This covers the edge case of team sizes that don’t divide evenly.
    """
    solver = create_solver(num_players=10, num_courts=2)
    round = solver.solve()
    assert len(round.matches) == 2
