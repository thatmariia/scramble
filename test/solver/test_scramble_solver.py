import logging
import pytest
import time

from scramble.core import Level, Court, Player, Round, HistoryManager
from scramble.solver import ScrambleSolver
from scramble.settings import Settings


def generate_players(count: int, level: Level, start_index: int = 1) -> list[Player]:
    """Generate a list of players with the given skill level and sequential IDs."""
    return [
        Player(name=f"Player {i + 1}", level=level, id=f"{i}")
        for i in range(start_index - 1, start_index - 1 + count)
    ]


def generate_courts(count: int) -> list[Court]:
    """Generate a list of court instances with unique IDs."""
    return [Court(name=f"Court {i + 1}", id=str(i + 1)) for i in range(count)]


def round_as_tuple_set(round: Round) -> frozenset[frozenset[frozenset[str]]]:
    """Convert a round into a nested frozenset structure to detect unique match configurations."""
    return frozenset(
        frozenset(frozenset(team.player_ids()) for team in match.teams)
        for match in round.matches
    )

def test_duplicate_ids():
    p1 = Player('', Level.BEGINNER, id='1')
    p2 = Player('', Level.BEGINNER, id='1')
    courts = generate_courts(1)

    with pytest.raises(ValueError, match=r".*Player IDs must be unique*"):
        ScrambleSolver([p1, p2], HistoryManager(), courts, Settings())

def test_no_courts():
    players = generate_players(10, Level.BEGINNER)
    courts = generate_courts(0)

    with pytest.raises(ValueError, match=r".*Courts may not be empty*"):
        ScrambleSolver(players, HistoryManager(), courts, Settings())


@pytest.mark.parametrize("num_matches", [1, 2, 10])
@pytest.mark.timeout(60)
def test_n_rounds_no_history(num_matches: int, caplog):
    """
    Ensure that each generated round has the correct number of matches and
    that each match consists of 2 teams with 4 players total.
    """
    caplog.set_level(logging.DEBUG)
    num_players = num_matches * 4
    num_courts = num_matches

    players = generate_players(num_players, Level.BEGINNER)
    courts = generate_courts(num_courts)
    solver = ScrambleSolver(players, HistoryManager(), courts, Settings())
    round = solver.solve()

    assert len(round.matches) == num_matches
    for match in round.matches:
        assert len(match.teams) == 2
        assert len(match.all_player_ids()) == 4


# @pytest.mark.repeat(1)
def test_1_rounds_mixed_levels_no_history(caplog):
    caplog.set_level(logging.INFO)
    players = (
        generate_players(6, Level.BEGINNER, start_index=1)
        + generate_players(1, Level.INTERMEDIATE, start_index=7)
        + generate_players(1, Level.EXPERT, start_index=8)
    )
    courts = generate_courts(2)

    solver = ScrambleSolver(players, HistoryManager(), courts, Settings())
    round = solver.solve()
    assert len(round.matches) == 2

    match_levels = []
    for match in round.matches:
        teams_levels = [
            sorted([player.level for player in team.players]) for team in match.teams
        ]
        match_levels.append(sorted(teams_levels))

    # Sort match_levels so we can reliably compare, regardless of match order
    match_levels = sorted(match_levels)

    expected = sorted(
        [
            sorted(
                [[Level.BEGINNER, Level.BEGINNER], [Level.BEGINNER, Level.BEGINNER]]
            ),
            sorted(
                [[Level.BEGINNER, Level.INTERMEDIATE], [Level.BEGINNER, Level.EXPERT]]
            ),
        ]
    )

    assert match_levels == expected


def test_1_match_5_rounds_with_history(caplog):
    """
    Ensure that solving the same scenario repeatedly with shared history yields
    a limited number of unique match configurations.
    """
    caplog.set_level(logging.DEBUG)
    num_players = 4
    num_courts = 1

    rounds = []
    history = HistoryManager()
    players = generate_players(num_players, Level.BEGINNER)
    courts = generate_courts(num_courts)

    for _ in range(4):
        solver = ScrambleSolver(players, history, courts, Settings())

        round = solver.solve()
        rounds.append(round_as_tuple_set(round))
        history.update_from_round(round)

        assert len(round.matches) == 1
        assert len(round.matches[0].teams) == 2
        assert len(round.matches[0].all_player_ids()) == 4

    expected_variants = 3
    assert len(set(rounds)) == expected_variants
    assert rounds[-1] in rounds[:expected_variants]


def test_1_qkotc_6_rounds_with_history(caplog):
    """
    Test match generation with 6 players, expecting 3v3 matches.
    Validate that a reasonable number of unique configurations are produced.
    """
    caplog.set_level(logging.DEBUG)
    num_players = 6
    num_courts = 1

    rounds = []

    players = generate_players(num_players, Level.BEGINNER)
    courts = generate_courts(num_courts)
    history = HistoryManager()

    for _ in range(6):
        solver = ScrambleSolver(players, history, courts, Settings())
        round = solver.solve()
        rounds.append(round_as_tuple_set(round))
        history.update_from_round(round)

        assert len(round.matches) == 1
        assert len(round.matches[0].teams) == 3
        assert len(round.matches[0].all_player_ids()) == 6

    assert len(set(rounds)) in [5, 6]


def test_2_matches_2_levels_no_history(caplog):
    """
    Ensure players of different levels are split into separate matches.
    """
    caplog.set_level(logging.DEBUG)
    players = generate_players(4, Level.BEGINNER, start_index=1) + generate_players(
        4, Level.INTERMEDIATE, start_index=5
    )
    courts = generate_courts(2)

    solver = ScrambleSolver(players, HistoryManager(), courts, Settings())
    round = solver.solve()

    assert len(round.matches) == 2
    for match in round.matches:
        avg_team_levels = {
            sum(player.level for player in team.players) / len(team.players)
            for team in match.teams
        }
        assert len(avg_team_levels) == 1


def test_1_qkotc_match_3_levels_no_history(caplog):
    """
    Ensure players of different levels are split into separate matches.
    """
    caplog.set_level(logging.DEBUG)
    players = (
        generate_players(2, Level.BEGINNER, start_index=1)
        + generate_players(3, Level.INTERMEDIATE, start_index=5)
        + generate_players(1, Level.EXPERT, start_index=10)
    )
    courts = generate_courts(1)

    solver = ScrambleSolver(players, HistoryManager(), courts, Settings())
    round = solver.solve()

    assert len(round.matches) == 1
    for match in round.matches:
        avg_team_levels = {
            sum(player.level for player in team.players) / len(team.players)
            for team in match.teams
        }
        assert len(avg_team_levels) == 2


def test_8_matches_with_history(caplog):
    caplog.set_level(logging.DEBUG)

    players = (
        generate_players(4, Level.BEGINNER, start_index=1)
        + generate_players(6, Level.IMPROVER, start_index=11)
        + generate_players(6, Level.INTERMEDIATE, start_index=21)
        + generate_players(5, Level.ADVANCED, start_index=31)
        + generate_players(5, Level.EXPERT, start_index=41)
    )
    courts = generate_courts(8)

    history = HistoryManager()

    rounds = []
    last_round = None
    num_rounds = 10
    for i in range(num_rounds):
        solver = ScrambleSolver(
            players, history, courts, Settings(), prev_round=last_round
        )
        start = time.time()
        round = solver.solve()
        last_round = round
        rounds.append(round_as_tuple_set(round))
        history.update_from_round(round)
        end = time.time()
        print(
            f"[{test_8_matches_with_history.__name__}] num_histories: {i} time: {end - start}"
        )

        assert len(round.matches) == 6

    expected_variants = num_rounds
    assert len(set(rounds)) == expected_variants


def test_15_matches_with_history(caplog):
    caplog.set_level(logging.DEBUG)

    players = (
        generate_players(10, Level.BEGINNER, start_index=1)
        + generate_players(10, Level.IMPROVER, start_index=11)
        + generate_players(20, Level.INTERMEDIATE, start_index=21)
        + generate_players(15, Level.ADVANCED, start_index=41)
        + generate_players(7, Level.EXPERT, start_index=61)
    )
    courts = generate_courts(16)

    history = HistoryManager()

    rounds = []
    last_round = None
    num_rounds = 5
    for i in range(num_rounds):
        solver = ScrambleSolver(
            players, history, courts, Settings(), prev_round=last_round
        )
        start = time.time()
        round = solver.solve()
        last_round = round
        rounds.append(round_as_tuple_set(round))
        history.update_from_round(round)
        end = time.time()
        print(
            f"[{test_15_matches_with_history.__name__}] num_histories: {i} time: {end - start}"
        )

        assert len(round.matches) == 15

    expected_variants = num_rounds
    assert len(set(rounds)) == expected_variants

def test_1_match_with_5_levels(caplog):
    caplog.set_level(logging.DEBUG)
    players = (
            generate_players(4, Level.BEGINNER, start_index=1)
            + generate_players(4, Level.IMPROVER, start_index=5)
            + generate_players(4, Level.INTERMEDIATE, start_index=9)
            + generate_players(4, Level.ADVANCED, start_index=13)
            + generate_players(4, Level.EXPERT, start_index=17)
        )
    courts = generate_courts(7)
    solver = ScrambleSolver(players, HistoryManager(), courts, Settings())
    round = solver.solve()

    assert len(round.matches) == 5
    for match in round.matches:
        levels = {player.level for team in match.teams for player in team.players}
        assert len(levels) == 1

def test_1_match_with_history_and_pause(caplog):
    caplog.set_level(logging.DEBUG)
    players = generate_players(5, Level.BEGINNER, start_index=1)

    courts = generate_courts(1)
    history = HistoryManager()

    # make a match with 5 players
    solver = ScrambleSolver(players, history, courts, Settings())
    round_1 = solver.solve()
    history.update_from_round(round_1)

    assert len(round_1.matches) == 1
    assert len(round_1.matches[0].all_player_ids()) == 5

    # one player will take a break
    solver = ScrambleSolver(
        players[:4], history, courts, Settings(), prev_round=round_1
    )
    round_2 = solver.solve()
    history.update_from_round(round_1)

    assert len(round_2.matches) == 1
    assert len(round_2.matches[0].all_player_ids()) == 4

    # player joined again
    solver = ScrambleSolver(players, history, courts, Settings(), prev_round=round_2)
    round_3 = solver.solve()
    history.update_from_round(round_3)

    assert len(round_3.matches) == 1
    assert len(round_3.matches[0].all_player_ids()) == 5
    assert round_as_tuple_set(round_1) != round_as_tuple_set(round_3)


@pytest.mark.timeout(60)
def test_1_qkotc_and_1_normal_match():
    """
    Test with 10 players and 2 courts, expecting 2 matches with correct distribution.
    This covers the edge case of team sizes that don’t divide evenly.
    """
    num_players = 10
    num_courts = 2

    players = generate_players(num_players, Level.BEGINNER)
    courts = generate_courts(num_courts)
    solver = ScrambleSolver(players, HistoryManager(), courts, Settings())
    round = solver.solve()
    assert len(round.matches) == 2
