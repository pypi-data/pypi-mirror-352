from sqlalchemy import delete

from leaguemanager.core.toolbox import clear_table
from leaguemanager.models import League, Season
from leaguemanager.services import LeagueSyncService, SeasonSyncService


def test_create_many_season(session, season_service) -> Season:
    # clear_table(session, Season)
    season_data = [
        {"name": "Test Create Season", "description": "Test Description", "projected_start_date": "2022-01-01"},
        {"name": "Test Create Season 2", "description": "Test Description 2", "projected_start_date": "2022-01-02"},
        {"name": "Test Create Season 3", "description": "Test Description 3", "projected_start_date": "2022-01-03"},
    ]

    seasons = season_service.create_many(season_data)

    assert seasons[0].name == "Test Create Season"
    assert seasons[1].name == "Test Create Season 2"
    assert seasons[2].name == "Test Create Season 3"

    clear_table(session, Season)


def test_attach_season_to_league(session, season_service, league_service) -> None:
    season_data = {
        "name": "SZNZ",
        "description": "I Want A Dog",
        "projected_start_date": "2025-01-01",
    }
    league_data = {
        "name": "Songs",
        "description": "I do a sport",
        "sport": "Music",
    }

    season = season_service.create(data=season_data, auto_commit=True)
    league = league_service.create(data=league_data, auto_commit=True)

    league = league_service.get_one_or_none(name="Songs")

    league.season = season

    league_service.update(league, auto_commit=True)

    new_league_call = league_service.get_one_or_none(name="Songs")
    assert new_league_call.season.name == "SZNZ"
    assert season.leagues[0].name == "Songs"

    clear_table(session, League)
    clear_table(session, Season)


def test_select_only_active_seasons(session, season_service) -> None:
    active_season = Season(
        name="Active Season-test",
        description="I Want A Dog",
        projected_start_date="2025-01-01",
        active=True,
    )

    inactive_season = Season(
        name="Inactive Season-test",
        description="I Want A Dog",
        projected_start_date="2025-01-01",
        active=False,
    )

    season_service.create_many([active_season, inactive_season])

    seasons = season_service.get_active_seasons()

    assert len(seasons) == 1
    assert seasons[0].name == "Active Season-test"

    clear_table(session, Season)
