import typer
from scramble.services import handlers

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
    court = handlers.add_court(name)
    typer.secho(f"Added court #{court.id}: {court.name}", fg=typer.colors.GREEN)


@court_app.command("remove")
def remove_court(court_id: str):
    """
    Remove a court by ID.

    Parameters
    ----------
    court_id : str
        ID of the court to remove.
    """
    handlers.remove_court(court_id)
    typer.secho(f"Removed court with ID {court_id}", fg=typer.colors.YELLOW)


@court_app.command("list")
def list_courts():
    """
    List all courts in the current session.
    """
    courts = handlers.list_courts()

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
    handlers.clear_courts()
    typer.secho("All courts have been cleared.", fg=typer.colors.YELLOW)
