import pytest

from scramble.core.level import Level
from scramble.core.player import Player
from scramble.core.team import Team


def test_player_ids():

    team = Team()
    assert team.player_ids() == set()

    team = Team.from_player_ids([], {})
    assert team.player_ids() == set()

    player1 = Player(1, 'Bob', Level.BEGINNER, "1")
    player2 = Player(2, 'Alice', Level.BEGINNER, "2")
    player3 = Player(3, 'Sacha', Level.BEGINNER, "3")
    player4 = Player(4, 'Alex', Level.BEGINNER, "4")

    lookup = { player.id: player for player in [player1, player2, player3, player4]}
    team = Team.from_player_ids([1, 2, 3], lookup)

    assert team.player_ids() == { 1, 2, 3 }

def test_avg_level():

    team = Team()
    assert team.avg_level() == 0.0

    team = Team.from_player_ids([], {})
    assert team.avg_level() == 0.0

    player1 = Player(1, 'Bob', Level.BEGINNER, "1")
    player2 = Player(2, 'Alice', Level.BEGINNER, "2")
    player3 = Player(3, 'Sacha', Level.BEGINNER, "3")
    player4 = Player(4, 'Alex', Level.BEGINNER, "4")

    lookup = { player.id: player for player in [player1, player2, player3, player4]}
    team = Team.from_player_ids([1, 2, 3, 4], lookup)
    assert team.avg_level() == Level.BEGINNER

    player4.level = Level.ADVANCED
    assert team.avg_level() == (Level.BEGINNER * 3 + Level.ADVANCED) / 4

