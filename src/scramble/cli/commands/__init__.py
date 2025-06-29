"""
CLI subcommands for the scramble project.

Each subcommand is a Typer app
that gets registered with the main CLI in main.py.
"""

from .player import player_app
from .court import court_app
from .round import round_app
from .session import session_app

__all__ = [
    "player_app",
    "court_app",
    "round_app",
    "session_app",
]
