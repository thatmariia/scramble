from datetime import datetime
from pathlib import Path


class SessionNameManager:
    SESSIONS_DIR = Path(__file__).resolve().parents[3] / "sessions_data"

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
