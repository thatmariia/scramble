import typer
import json
from pathlib import Path
from scramble.app.app_session import AppSession
from scramble.app.session_persistence import SessionPersistence, SessionNameManager
from scramble.settings import Settings
from scramble.cli.state import set_current_session
from scramble.cli.utils import require_session

session_app = typer.Typer(help="Manage application sessions")


@session_app.command("new")
def new_session(
    name: str = typer.Option(None, help="Optional name for the new session."),
    settings_path: Path = typer.Option(None, help="Path to a JSON settings file.")
):
    """
    Start a new session with the given name and settings.

    Parameters
    ----------
    name : str, optional
        The name of the new session. If not provided, a default name will be generated.
    settings_path : Path, optional
        Path to a JSON file containing settings. If not provided, default settings will be used.
    """
    if settings_path and settings_path.is_file():
        with open(settings_path, "r") as f:
            settings = Settings.from_dict(json.load(f))
    else:
        typer.secho("Using default settings as no valid settings file was provided.", fg=typer.colors.YELLOW)
        settings = Settings()

    session_name = name or SessionNameManager.generate_name()
    session = AppSession(settings=settings, session_name=session_name)
    set_current_session(session)

    SessionPersistence.save(session)
    typer.secho(f"Started new session: {session.session_name}", fg=typer.colors.GREEN)


@session_app.command("load")
def load_session(
    name: str = typer.Option(None, help="Name of the session to load. If omitted, loads the latest.")
):
    """
    Load an existing session by name or the latest session if no name is provided.

    Parameters
    ----------
    name : str, optional
        The name of the session to load. If not provided, the latest session will be loaded.
    """
    session = SessionPersistence.load(name)
    if session is None:
        typer.secho("No session found.", fg=typer.colors.RED)
        raise typer.Exit(code=1)
    set_current_session(session)
    typer.secho(f"Loaded session: {session.session_name}", fg=typer.colors.GREEN)


@session_app.command("save")
def save_session():
    """
    Save the current session to disk.
    """
    session = require_session()
    SessionPersistence.save(session)
    typer.secho(f"Session '{session.session_name}' saved successfully.", fg=typer.colors.GREEN)


@session_app.command("default-settings")
def export_default_settings(path: Path = typer.Argument(..., help="Where to write the settings JSON")):
    """
    Export default settings to a JSON file.

    Parameters
    ----------
    path : Path
        The file path where the default settings will be written.
    """
    settings = Settings()
    ROOT = Path(__file__).resolve().parents[4]
    path = ROOT / path
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(settings.to_dict(), f, indent=4)
    typer.echo(f"Default settings written to {path}")
