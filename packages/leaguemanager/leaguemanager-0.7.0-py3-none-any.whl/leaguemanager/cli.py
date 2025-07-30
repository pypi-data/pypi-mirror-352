"""CLI for League Manager tool."""

import json
from typing import Annotated, Optional

import typer
from advanced_alchemy.exceptions import DuplicateKeyError
from rich import print
from rich.prompt import Prompt
from sqlalchemy import delete
from sqlalchemy.orm import Session

from leaguemanager import models
from leaguemanager.core import get_settings
from leaguemanager.db import register_sqlite
from leaguemanager.db.cli.alembic_cli import db_app
from leaguemanager.dependency.cli_callbacks import (
    provide_manager_service,
    provide_sync_db_session,
)
from leaguemanager.services import LeagueSyncService, ScheduleSyncService, SeasonSyncService, TeamSyncService

from . import __app_name__, __version__

settings = get_settings()
register_sqlite()

app = typer.Typer()


def _version_callback(value: bool) -> None:
    if value:
        print(f"{__app_name__} v{__version__}")
        raise typer.Exit()


@app.command(help="Populate the database with synthetic data.")
def populate(
    season_service: Annotated[
        Optional[SeasonSyncService], typer.Argument(callback=provide_manager_service, parser=SeasonSyncService)
    ] = None,
    league_service: Annotated[
        Optional[LeagueSyncService], typer.Argument(callback=provide_manager_service, parser=LeagueSyncService)
    ] = None,
    team_service: Annotated[
        Optional[TeamSyncService], typer.Argument(callback=provide_manager_service, parser=TeamSyncService)
    ] = None,
    schedule_service: Annotated[
        Optional[ScheduleSyncService], typer.Argument(callback=provide_manager_service, parser=ScheduleSyncService)
    ] = None,
) -> None:
    if (settings.APP_DIR / "example_data.json").exists():
        with open(settings.APP_DIR / "example_data.json") as _data:
            data = json.load(_data)
    elif not (settings.SYNTH_DATA_DIR / "example_data.json").exists():
        data_file = Prompt.ask("Please provide the path to the data directory: ")
        try:
            with open(data_file) as _data:
                data = json.load(_data)
        except FileNotFoundError:
            print(f"File {data_file} does not exist.")
            return
    else:
        with open(settings.SYNTH_DATA_DIR / "example_data.json") as _data:
            data = json.load(_data)
    try:
        season_service.create_many(data["seasons"], auto_commit=True)
        league_service.create_many(data["leagues"], auto_commit=True)
        team_service.create_many(data["teams"], auto_commit=True)
        schedule_service.create_many(data["schedules"], auto_commit=True)
    except DuplicateKeyError:
        print("[red]Data already exists in the database. Will not create any data...[/red]")
        return

    print(
        "✨ [green]Successfully created data![/green] ✨",
        f"\nCreated {season_service.count()} Seasons",
        f"\nCreated {league_service.count()} Leagues",
        f"\nCreated {team_service.count()} Teams",
        f"\nCreated {schedule_service.count()} Schedules",
    )
    return


@app.command(help="Check the counts of data in each table.")
def check(
    session: Annotated[Optional[Session], typer.Argument(callback=provide_sync_db_session, parser=Session)] = None,
    season_service: Annotated[
        Optional[SeasonSyncService], typer.Argument(callback=provide_manager_service, parser=SeasonSyncService)
    ] = None,
    league_service: Annotated[
        Optional[LeagueSyncService], typer.Argument(callback=provide_manager_service, parser=LeagueSyncService)
    ] = None,
    team_service: Annotated[
        Optional[TeamSyncService], typer.Argument(callback=provide_manager_service, parser=TeamSyncService)
    ] = None,
    schedule_service: Annotated[
        Optional[ScheduleSyncService],
        typer.Argument(callback=provide_manager_service, parser=ScheduleSyncService),
    ] = None,
    all: bool = typer.Option(
        False,
        "--all",
        "-a",
        help="Check all seasons, leagues, and teams.",
    ),
) -> None:
    if all:
        print(
            "✨ [green]These are the counts of data in each table[/green] ✨",
            f"\n{season_service.count()} Seasons",
            f"\n{league_service.count()} Leagues",
            f"\n{team_service.count()} Teams",
            f"\n{schedule_service.count()} Schedules",
        )
    else:
        model = Prompt.ask("Please provide the model name to check (i.e. Season): ")
        try:
            _models = session.query(getattr(models, model)).all()
            print(f"Found {session.query(getattr(models, model)).count()} {model}s.")
            for m in _models:
                if m.name:
                    print(f">> {m.name}")
        except AttributeError:
            print(f"Model [green]{model}[/green] does not exist.")
    return


@app.command(name="delete", help="Delete data from the database.")
def _delete(
    session: Annotated[Optional[Session], typer.Argument(callback=provide_sync_db_session, parser=Session)] = None,
    all: bool = typer.Option(
        False,
        "--all",
        "-a",
        help="Delete all seasons, leagues, teams, and schedules.",
    ),
) -> None:
    if all:
        session.execute(delete(models.Season))
        session.execute(delete(models.League))
        session.execute(delete(models.Team))
        session.execute(delete(models.Schedule))
        session.commit()
        print("⛔ [yellow]Removed all Seasons, Leagues, Teams, and Schedules.[/yellow]⛔")
    else:
        model = Prompt.ask("Please provide the model name to delete (i.e. Season): ")
        try:
            session.execute(delete(getattr(models, model.title())))
            session.commit()
        except AttributeError:
            print(f"Model [green]{model.title()}[/green] does not exist.")
        print(f"⛔ [yellow]Removed all data in the {model.title()} table.[/yellow]⛔")
    return


@app.callback(no_args_is_help=True, help="League Manager CLI.")
def main(
    ctx: typer.Context,
    version: Annotated[
        Optional[bool],
        typer.Option(
            "--version",
            "-V",
            callback=_version_callback,
            is_eager=True,
            help="Show the version and exit.",
        ),
    ] = None,
):
    """League Manager CLI."""
    return


# This creates an app for Typer, adding the above commands.
# This enables us to add the `db_app`, which is a Click group from Advanced Alchemy.
app = typer.main.get_command(app)
app.add_command(db_app)
