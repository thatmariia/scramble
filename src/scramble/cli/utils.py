import typer
from scramble.cli.state import get_current_session
from scramble.app import AppSession


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
    return session