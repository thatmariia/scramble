from datetime import datetime
from pathlib import Path


class SessionNameManager:
    SESSIONS_DIR = Path(__file__).resolve().parents[3] / "sessions_data"
    LATEST_FILE = SESSIONS_DIR / "latest.txt"

    @staticmethod
    def generate_name() -> str:
        """
        Generates a session name based on the current date and time.

        Returns
        -------
        str
            A string representing the current date and time in the format "YYYY-MM-DD_HH-MM-SS".
        """
        return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    @classmethod
    def get_latest(cls) -> str:
        """
        Retrieves the name of the latest session from the latest file.

        Returns
        -------
        str
            The name of the latest session.

        Raises
        -------
        FileNotFoundError
            If the latest session file does not exist.
        """
        try:
            with open(cls.LATEST_FILE, "r") as f:
                return f.read().strip()
        except FileNotFoundError:
            raise FileNotFoundError(f"No latest session found at {cls.LATEST_FILE}.")

    @classmethod
    def set_latest(cls, session_name: str):
        """
        Sets the latest session name in the latest file.
        """
        cls.SESSIONS_DIR.mkdir(parents=True, exist_ok=True)
        with open(cls.LATEST_FILE, "w") as f:
            f.write(session_name)