import pytest

from scramble.core.level import Level
from scramble.core.team import Team
from scramble.core.court import Court
from scramble.core.player import Player
from scramble.core.match import Match
from scramble.core.round import Round


def test_partner_pairs():
    empty = Round([])
    assert list(empty.partner_pairs()) == []

    player1 = Player(1, 'Bob', Level.BEGINNER, "1")
    player2 = Player(2, 'Alice', Level.BEGINNER, "2")
    player3 = Player(3, 'Sacha', Level.BEGINNER, "3")
    player4 = Player(4, 'Alex', Level.BEGINNER, "4")

    team1 = Team([player1, player2])
    team2 = Team([player3, player4])

    court1 = Court(1, '1')

    match1 = Match([team1, team2], court1)
    round = Round([match1])

    assert list(round.partner_pairs()) == [(1, 2), (2, 1), (3, 4), (4, 3)]

    player5 = Player(5, 'Pietje', Level.INTERMEDIATE, "5")
    team1.players.append(player5)

    assert list(round.partner_pairs()) == [
        (1, 2), (2, 1), (1, 5), (5, 1), (2, 5), (5, 2), (3, 4), (4, 3)]


def test_opponent_pairs():
    empty = Round([])
    assert list(empty.opponent_pairs()) == []

    player1 = Player(1, 'Bob', Level.BEGINNER, "1")
    player2 = Player(2, 'Alice', Level.BEGINNER, "2")
    player3 = Player(3, 'Sacha', Level.BEGINNER, "3")
    player4 = Player(4, 'Alex', Level.BEGINNER, "4")

    team1 = Team([player1, player2])
    team2 = Team([player3, player4])

    court1 = Court(1, '1')

    match1 = Match([team1, team2], court1)
    round = Round([match1])

    assert list(round.opponent_pairs()) == [
        (1, 3), (3, 1), (1, 4), (4, 1), (2, 3), (3, 2), (2, 4), (4, 2)]

    player5 = Player(5, 'Pietje', Level.INTERMEDIATE, "5")
    team1.players.append(player5)

    print(list(round.opponent_pairs()))
    assert list(round.opponent_pairs()) == [(1, 3), (3, 1), (1, 4), (4, 1), (
        2, 3), (3, 2), (2, 4), (4, 2), (5, 3), (3, 5), (5, 4), (4, 5)]
