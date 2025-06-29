import typer
from scramble.core import Court
from scramble.cli.utils import require_session
from scramble.cli.state import set_current_session

court_app = typer.Typer(help="Manage courts")


@court_app.command("add")
def add_court(name: str):
    """
    Add a new court to the current session.

    Parameters
    ----------
    name : str
        Name of the court.
    """
    session = require_session()

    court = Court(name=name)
    session.court_state.add(court)
    typer.secho(f"Added court #{court.id}: {court.name}", fg=typer.colors.GREEN)

    set_current_session(session)


@court_app.command("remove")
def remove_court(court_id: int):
    """
    Remove a court by ID.

    Parameters
    ----------
    court_id : int
        ID of the court to remove.
    """
    session = require_session()
    session.court_state.remove(court_id)
    typer.secho(f"Removed court with ID {court_id}", fg=typer.colors.YELLOW)

    set_current_session(session)


@court_app.command("list")
def list_courts():
    """
    List all courts in the current session.
    """
    session = require_session()
    courts = session.court_state.courts_list()

    if not courts:
        typer.secho("No courts have been added yet.", fg=typer.colors.RED)
        return

    typer.secho("Courts:", fg=typer.colors.BLUE)
    for court in courts:
        typer.echo(f" - {court}")


@court_app.command("clear")
def clear_courts():
    """
    Clear all courts from the current session.
    """
    session = require_session()
    session.court_state.clear()
    typer.secho("All courts have been cleared.", fg=typer.colors.YELLOW)

    set_current_session(session)
