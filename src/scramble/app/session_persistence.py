import json
from scramble.app.app_session import AppSession
from scramble.settings import Settings
from scramble.app.player_state import PlayerState
from scramble.app.court_state import CourtState
from scramble.app.round_tracker import RoundTracker
from scramble.app.session_name_manager import SessionNameManager

SESSIONS_DIR = SessionNameManager.SESSIONS_DIR


class SessionPersistence:
    """
    Handles the persistence of AppSession objects to disk.
    This class is responsible for saving and loading session data.
    """

    @staticmethod
    def save(session: AppSession):
        """
        Saves the given AppSession to disk.

        Parameters
        ----------
        session : AppSession
            The session to save.
        """
        session_data = session.to_dict()

        path = SESSIONS_DIR / session.session_name
        path.mkdir(parents=True, exist_ok=True)

        for filename, data in session_data.items():
            if not hasattr(data, "to_dict"):
                continue
            file_path = path / f"{filename}.json"
            with open(file_path, "w") as f:
                json.dump(data.to_dict(), f, indent=4)

    @staticmethod
    def load(session_name: str) -> AppSession:
        """
        Loads an AppSession from disk.

        Parameters
        ----------
        session_name : str | None = None
            The name of the session to load.
            If None, the latest session will be loaded.

        Returns
        -------
        AppSession | None
            The loaded AppSession object, or None if the session does not exist.
        """
        path = SESSIONS_DIR / session_name
        if not path.exists():
            raise FileNotFoundError(f"Session {session_name} not found")

        with open(path / "settings.json", "r") as f:
            settings = Settings.from_dict(json.load(f))

        app_session = AppSession(settings, session_name)

        with open(path / "player_state.json", "r") as f:
            app_session.player_state = PlayerState.from_dict(json.load(f))
        with open(path / "court_state.json", "r") as f:
            app_session.court_state = CourtState.from_dict(json.load(f))
        with open(path / "round_tracker.json", "r") as f:
            app_session.round_tracker = RoundTracker.from_dict(json.load(f))

        return app_session

    @staticmethod
    def list_session_names() -> list[str]:
        """
        Return the names of all sessions available to load.

        Returns:
            list[str]: list of session names
        """
        return [p.name for p in SESSIONS_DIR.iterdir() if p.is_dir()]

    @staticmethod
    def exists(session_name: str) -> bool:
        """
        Check if a session with the given name already exists.

        Parameters
        ----------
        session_name : str
            The name of the session to check.

        Returns
        -------
        bool
            True if the session exists, False otherwise.
        """
        return (SESSIONS_DIR / session_name).exists()
