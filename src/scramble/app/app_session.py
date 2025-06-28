from scramble.settings import Settings
from scramble.app.court_state import CourtState
from scramble.app.player_state import PlayerState
from scramble.app.round_tracker import RoundTracker
from scramble.solver import ScrambleSolver
from scramble.core import Round


class AppSession:
    """
    Represents a session for the Scramble app.
    This class is used to manage the state of the application during a session.

    Attributes
    ----------
    settings : Settings
        The settings for the Scramble app.
    player_state : PlayerState
        The state of players in the Scramble app.
    court_state : CourtState
        The state of courts in the Scramble app.
    round_tracker : RoundTracker
        The round tracker for managing rounds played in the Scramble app.
    session_name : str
        The name of the session.
    """

    def __init__(self, settings: Settings, session_name: str):
        """
        Initializes the AppSession with the given settings.

        Parameters
        ----------
        settings : Settings
            The settings for the Scramble app.
        session_name : str
            The name of the session.
        """
        self.settings = settings
        self.player_state = PlayerState()
        self.court_state = CourtState()
        self.round_tracker = RoundTracker()

        self.session_name = session_name

    def clear(self):
        """
        Clears the session state, including player state, court state, and round tracker.
        """
        self.player_state.clear()
        self.court_state.clear()
        self.round_tracker.clear()

    def get_new_round(self):
        solver = ScrambleSolver(
            active_players=self.player_state.active_list(),
            history=self.round_tracker.history_manager,
            courts=self.court_state.courts_list(),
            settings=self.settings,
        )
        game_round = solver.solve()
        return game_round

    def start_round(self, game_round: Round):
        """
        Starts a new round by adding it to the round tracker and updating player states.

        Parameters
        ----------
        game_round : Round
            The round to be started.
        """
        self.round_tracker.add_round(game_round)
