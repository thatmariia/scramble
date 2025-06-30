import datetime
import typer
from scramble.cli.state import get_current_session
from scramble.cli.logging import configure_logging
from scramble.app import AppSession
from scramble.app.session_name_manager import SessionNameManager

def require_session() -> AppSession:
    """
    Ensure that a session is currently active. If not, print an error message and exit.

    Returns
    -------
    AppSession
        The current active session.

    Raises
    ------
    typer.Exit
        If no session is active, exits with an error message.
    """
    session = get_current_session()
    if not session:
        typer.secho("No session is active. Load or start a session first.", fg=typer.colors.RED)
        raise typer.Exit(1)

    log_dir = SessionNameManager.SESSIONS_DIR / session.session_name
    log_file = log_dir / datetime.datetime.now().strftime("logfile_%H_%M_%d_%m_%Y.log")
    configure_logging(log_file, session.settings.log_verbose, not session.settings.log_enabled)
    return session
