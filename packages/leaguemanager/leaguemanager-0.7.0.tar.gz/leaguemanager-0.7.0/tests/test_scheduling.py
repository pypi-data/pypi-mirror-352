from datetime import datetime

import pytest

from leaguemanager.core.toolbox import clear_table
from leaguemanager.domain import Scheduler, StandingsTable
from leaguemanager.models import Fixture, League, Schedule, Season, Team

season_data = {
    "name": "Season Scheduler Test",
    "description": "Burndt",
    "projected_start_date": "2022-01-01",
}

league_data = {
    "name": "League Scheduler Test",
}

schedule_data = {
    "name": "Schedule for Test Scheduler",
    "total_games": 10,
    "start_date": "2025-1-05 08:00:00",
}


@pytest.fixture(scope="module")
def season():
    return Season(**season_data)


@pytest.fixture(scope="module")
def league():
    return League(**league_data)


@pytest.fixture(scope="module")
def teams(all_teams):
    return [Team(**team_data) for team_data in all_teams]


@pytest.fixture(scope="module")
def sunday_schedule(season, league):
    schedule = Schedule(
        league_id=league.id,
        season_id=season.id,
        name="Schedule for Test Scheduler",
        total_games=10,
        start_date="2025-1-05 08:00:00",
        concurrent_games=2,
    )

    return schedule


@pytest.fixture(scope="module")
def scheduler(session, sunday_schedule) -> Scheduler:
    scheduler = Scheduler(session=session, schedule=sunday_schedule)
    return scheduler


def test_generator_split_teams_even(scheduler, teams):
    split_teams = scheduler.generator.split_teams(teams)

    assert split_teams == (teams[:4], teams[4:])


def test_generator_split_teams_odd(scheduler, teams):
    temp_remove_team = teams.pop()

    assert len(teams) == 7

    with pytest.raises(ValueError):
        _ = scheduler.generator.split_teams(teams)

    teams.append(temp_remove_team)


@pytest.mark.parametrize("matchday", [1, 2, 3])
def test_generator_create_matchups_first_matchday(scheduler, matchday, teams):
    matchups = scheduler.generator.create_matchups(matchday=matchday, teams=teams)
    assert len(matchups) == 4


def test_increment_matchday(scheduler):
    matchday_1_start_time = scheduler.generator.increment_matchday(matchday=1)
    matchday_2_start_time = scheduler.generator.increment_matchday(matchday=2)

    assert matchday_1_start_time == datetime(2025, 1, 5, 8, 0)
    assert matchday_2_start_time == datetime(2025, 1, 12, 8, 0)


@pytest.mark.parametrize(
    "count, concurrent, expected",
    [(1, 2, "A"), (2, 2, "B"), (3, 4, "C"), (4, 4, "D"), (2, 1, "A"), (3, 1, "A")],
)
def test_determine_field(scheduler, count, concurrent, expected):
    field = scheduler.generator.determine_field(count, concurrent)
    assert field == expected


def test_home_or_away_even_round(scheduler, all_teams):
    fake_match = (all_teams[0], all_teams[1])

    home, away = scheduler.generator.home_or_away(round_number=2, match=fake_match)
    assert home == all_teams[0]
    assert away == all_teams[1]


def test_home_or_away_odd_round(scheduler, all_teams):
    fake_match = (all_teams[0], all_teams[1])

    home, away = scheduler.generator.home_or_away(round_number=1, match=fake_match)
    assert home == all_teams[1]
    assert away == all_teams[0]


@pytest.mark.parametrize(
    "_concurrent, _matchday, _match_count, expected",
    [
        (1, 1, 1, datetime(2025, 1, 5, 8, 0)),
        (1, 1, 2, datetime(2025, 1, 5, 10, 0)),
        (1, 1, 3, datetime(2025, 1, 5, 12, 0)),
        (1, 1, 4, datetime(2025, 1, 5, 14, 0)),
        (1, 1, 5, datetime(2025, 1, 5, 16, 0)),
        (1, 2, 1, datetime(2025, 1, 12, 8, 0)),
        (1, 2, 3, datetime(2025, 1, 12, 12, 0)),
        (1, 2, 5, datetime(2025, 1, 12, 16, 0)),
        (2, 1, 1, datetime(2025, 1, 5, 8, 0)),
        (2, 1, 2, datetime(2025, 1, 5, 8, 0)),
        (2, 1, 3, datetime(2025, 1, 5, 10, 0)),
        (2, 1, 4, datetime(2025, 1, 5, 10, 0)),
        (2, 1, 5, datetime(2025, 1, 5, 12, 0)),
        (2, 1, 6, datetime(2025, 1, 5, 12, 0)),
        (3, 2, 1, datetime(2025, 1, 12, 8, 0)),
        (3, 3, 2, datetime(2025, 1, 19, 8, 0)),
        (3, 4, 3, datetime(2025, 1, 26, 8, 0)),
        (3, 5, 4, datetime(2025, 2, 2, 10, 0)),
        (3, 6, 7, datetime(2025, 2, 9, 12, 0)),
        (4, 1, 1, datetime(2025, 1, 5, 8, 0)),
        (4, 1, 4, datetime(2025, 1, 5, 8, 0)),
    ],
)
def test_determine_start_time_third_matchday(
    scheduler, sunday_schedule, _concurrent, _matchday, _match_count, expected
):
    sunday_schedule.concurrent_games = _concurrent
    start_time = scheduler.generator.determine_start_time(matchday=_matchday, match_count=_match_count)
    assert start_time == expected


def test_create_matchday_fixtures(scheduler, teams):
    fixtures = scheduler.generator.create_matchday_fixtures(matchday=1, round_number=1, teams=teams)
    assert len(fixtures) == 4


@pytest.mark.parametrize(["total_games", "expected"], [(8, 32), (10, 32), (15, 32), (16, 64), (20, 64), (24, 96)])
def test_generate_fixtures_eight_teams(scheduler, total_games, expected, teams):
    scheduler.generator.schedule.total_games = total_games
    fixtures = scheduler.generator.generate_fixtures(teams=teams)
    assert len(fixtures) == expected

    fixtures = scheduler.generator.generate_fixtures(shuffle_order=False, teams=teams)
    assert len(fixtures) == expected
    fixtures.clear()


@pytest.mark.parametrize(["total_games", "expected"], [(4, 8), (8, 16), (10, 16)])
def test_generate_fixtures_four_teams(scheduler, total_games, expected, teams):
    teams = teams[:4]

    scheduler.generator.schedule.total_games = total_games
    fixtures = scheduler.generator.generate_fixtures(teams=teams)
    assert len(fixtures) == expected

    fixtures = scheduler.generator.generate_fixtures(shuffle_order=False, teams=teams)
    assert len(fixtures) == expected
    fixtures.clear()


def test_generate_season_fixtures_too_few_teams(scheduler, session, teams):
    scheduler.generator.schedule.total_games = 3
    with pytest.raises(ValueError):
        scheduler.generate_fixtures(teams=teams)
    scheduler.generator.schedule.total_games = 10


def test_sort_fixtures_by_date(session, scheduler, season, league, teams):
    _schedule = Schedule(**schedule_data, season_id=season.id, league_id=league.id)
    scheduler = Scheduler(session=session, schedule=_schedule)

    fixtures = scheduler.generate_fixtures(teams=teams)
    _schedule.fixtures = fixtures

    assert fixtures[0].date == datetime(2025, 1, 5, 8, 0)
    assert fixtures[-1].date == datetime(2025, 2, 23, 10, 0)

    sorted_fixtures = scheduler.sort_fixtures(order_by_field="date", sort_order="desc")

    assert sorted_fixtures[0].date == datetime(2025, 2, 23, 10, 0)
    assert sorted_fixtures[-1].date == datetime(2025, 1, 5, 8, 0)


def test_push_fixture_to_end_of_schedule(session, scheduler, league, season, teams):
    clear_table(session, Fixture)

    _schedule = Schedule(
        league_id=league.id,
        season_id=season.id,
        name="Test Schedule",
        total_games=10,
        start_date="2025-1-05 08:00:00",
    )
    scheduler = Scheduler(session=session, schedule=_schedule)
    _fixtures = scheduler.generator.generate_fixtures(teams=teams)
    _schedule.fixtures = _fixtures

    fixtures = scheduler.schedule.fixtures

    assert len(fixtures) == 32
    assert fixtures[0].date == datetime(2025, 1, 5, 8, 0)
    assert fixtures[0].date == datetime(2025, 1, 5, 8, 0)
    assert fixtures[-1].date == datetime(2025, 2, 23, 10, 0)

    scheduler.push_fixture_to_end_of_schedule(fixtures[0])

    assert len(fixtures) == 32
    assert fixtures[0].date == datetime(2025, 3, 2, 8, 0)
    assert fixtures[1].date == datetime(2025, 1, 5, 8, 0)
    assert fixtures[-1].date == datetime(2025, 2, 23, 10, 0)


def test_push_matchday_to_end_of_schedule(session, scheduler, season, league, teams):
    _schedule = Schedule(
        league_id=league.id,
        season_id=season.id,
        name="Test Schedule",
        total_games=10,
        start_date="2025-1-05 08:00:00",
    )

    fixtures = scheduler.generator.generate_fixtures(teams=teams[:4])
    _schedule.fixtures = fixtures
    scheduler = Scheduler(session=session, schedule=_schedule)

    scheduler.sort_fixtures()

    assert fixtures[0].date == datetime(2025, 1, 5, 8, 0)
    assert fixtures[1].date == datetime(2025, 1, 5, 8, 0)
    assert fixtures[2].date == datetime(2025, 1, 12, 8, 0)
    assert fixtures[3].date == datetime(2025, 1, 12, 8, 0)
    assert fixtures[4].date == datetime(2025, 1, 19, 8, 0)
    assert fixtures[5].date == datetime(2025, 1, 19, 8, 0)
    assert fixtures[-1].date == datetime(2025, 2, 23, 8, 0)

    scheduler.push_matchday_to_end_of_schedule(2)

    assert fixtures[0].date == datetime(2025, 1, 5, 8, 0)
    assert fixtures[1].date == datetime(2025, 1, 5, 8, 0)
    assert fixtures[2].date == datetime(2025, 3, 2, 8, 0)
    assert fixtures[3].date == datetime(2025, 3, 2, 8, 0)
    assert fixtures[4].date == datetime(2025, 1, 19, 8, 0)
    assert fixtures[5].date == datetime(2025, 1, 19, 8, 0)
    assert fixtures[-1].date == datetime(2025, 2, 23, 8, 0)


def test_push_all_fixtures_by_one_week(session, scheduler, league, season, teams):
    _schedule = Schedule(
        league_id=league.id,
        season_id=season.id,
        name="Test Schedule",
        total_games=10,
        start_date="2025-1-05 08:00:00",
    )

    fixtures = scheduler.generator.generate_fixtures(teams=teams[:4])
    _schedule.fixtures = fixtures
    scheduler = Scheduler(session, schedule=_schedule)

    fixture = fixtures[4]  # Contains matchday 3 (1/19/2025)
    scheduler.push_all_fixtures_by_one_week(fixture)
    assert fixtures[0].date == datetime(2025, 1, 5, 8, 0)
    assert fixtures[1].date == datetime(2025, 1, 5, 8, 0)
    assert fixtures[2].date == datetime(2025, 1, 12, 8, 0)
    assert fixtures[3].date == datetime(2025, 1, 12, 8, 0)
    assert fixtures[4].date == datetime(2025, 1, 26, 8, 0)
    assert fixtures[5].date == datetime(2025, 1, 26, 8, 0)
    assert fixtures[6].date == datetime(2025, 2, 2, 8, 0)
    assert fixtures[7].date == datetime(2025, 2, 2, 8, 0)
    assert fixtures[-1].date == datetime(2025, 3, 2, 8, 0)
