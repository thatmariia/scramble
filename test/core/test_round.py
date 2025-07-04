import pytest

from scramble.core import Level, Team, Court, Player, Match, Round


def test_partner_pairs():
    empty = Round([])
    assert list(empty.partner_pairs()) == []

    player1 = Player('Bob', Level.BEGINNER, "1", id='1')
    player2 = Player('Alice', Level.BEGINNER, "2", id='2')
    player3 = Player('Sacha', Level.BEGINNER, "3", id='3')
    player4 = Player('Alex', Level.BEGINNER, "4", id='4')

    team1 = Team([player1, player2])
    team2 = Team([player3, player4])

    court1 = Court('1', id='1')

    match1 = Match([team1, team2], court1)
    round = Round([match1])

    assert sorted(round.partner_pairs()) == [
        ('1', '2'), ('2', '1'), ('3', '4'), ('4', '3')]

    player5 = Player('Pietje', Level.INTERMEDIATE, "5", id='5')
    team1.players.append(player5)

    assert sorted(round.partner_pairs()) == [('1', '2'), ('1', '5'), (
        '2', '1'), ('2', '5'), ('3', '4'), ('4', '3'), ('5', '1'), ('5', '2')]


def test_opponent_pairs():
    empty = Round([])
    assert list(empty.opponent_pairs()) == []

    player1 = Player('Bob', Level.BEGINNER, "1", id='1')
    player2 = Player('Alice', Level.BEGINNER, "2", id='2')
    player3 = Player('Sacha', Level.BEGINNER, "3", id='3')
    player4 = Player('Alex', Level.BEGINNER, "4", id='4')

    team1 = Team([player1, player2])
    team2 = Team([player3, player4])

    court1 = Court('1', id='1')

    match1 = Match([team1, team2], court1)
    round = Round([match1])

    assert sorted(round.opponent_pairs()) == [('1', '3'), ('1', '4'), (
        '2', '3'), ('2', '4'), ('3', '1'), ('3', '2'), ('4', '1'), ('4', '2')]

    player5 = Player('Pietje', Level.INTERMEDIATE, "5", id='5')
    team1.players.append(player5)

    assert sorted(round.opponent_pairs()) == [('1', '3'), ('1', '4'), ('2', '3'), ('2', '4'), (
        '3', '1'), ('3', '2'), ('3', '5'), ('4', '1'), ('4', '2'), ('4', '5'), ('5', '3'), ('5', '4')]
