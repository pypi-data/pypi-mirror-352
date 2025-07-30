from datetime import timedelta

from attrs import define, field
from sqlalchemy.orm import Session

from leaguemanager.models import Fixture, Schedule, Team
from leaguemanager.services import (
    FixtureSyncService,
    FixtureTeamSyncService,
    StandingsSyncService,
    TeamSyncService,
)

from ._generator import ScheduleGenerator

__all__ = ["Scheduler"]


@define
class Scheduler:
    session: Session
    schedule: Schedule
    generator: ScheduleGenerator = field(init=False)

    standings_service: StandingsSyncService = field(init=False)
    fixture_service: FixtureSyncService = field(init=False)
    fixture_team_service: FixtureTeamSyncService = field(init=False)
    team_service: TeamSyncService = field(init=False)

    def __attrs_post_init__(self):
        # if not self.schedule.fixtures:
        #     raise ValueError("No fixtures found for schedule")
        self.standings_service = StandingsSyncService(session=self.session)
        self.fixture_service = FixtureSyncService(session=self.session)
        self.fixture_team_service = FixtureTeamSyncService(session=self.session)
        self.team_service = TeamSyncService(session=self.session)
        self.generator = ScheduleGenerator(schedule=self.schedule)

    def sort_fixtures(self, order_by_field: str = "date", sort_order: str = "asc"):
        sorted_fixtures = sorted(
            self.schedule.fixtures,
            key=lambda fixture: getattr(fixture, order_by_field),
            reverse=(sort_order == "desc"),
        )
        return sorted_fixtures

    @property
    def last_fixture(self):
        return self.sort_fixtures(order_by_field="date", sort_order="desc")[0]

    def push_fixture_to_end_of_schedule(self, fixture: Fixture):
        matchday_diff = (self.last_fixture.matchday + 1) - fixture.matchday
        fixture.date = fixture.date + timedelta(days=matchday_diff * 7)
        return fixture

    def push_matchday_to_end_of_schedule(self, matchday: int):
        last_fixture_matchday = self.last_fixture.matchday
        for fixture in self.schedule.fixtures:
            if fixture.matchday == matchday:
                matchday_diff = last_fixture_matchday + 1 - fixture.matchday
                fixture.date = fixture.date + timedelta(days=matchday_diff * 7)

    def push_all_fixtures_by_one_week(self, fixture: Fixture):
        # Push all fixtures by one week with date after the fixture
        for f in self.schedule.fixtures:
            if f.matchday >= fixture.matchday:
                f.date = f.date + timedelta(days=7)
        return fixture

    def generate_fixtures(self, shuffle_order: bool = True, teams: list[Team] | None = None, **kwargs) -> list[Fixture]:
        """Generates fixtures for the entire season.

        Included here for convenience, but can be accessed through the `generator` attribute
        as well.

        Args:
            shuffle_order (bool, optional): Determines whether fixtures will be randomized. Defaults to True.
            teams (list[Team], optional): Teams specific to the schedule/league. Defaults to None.
        """
        generator = ScheduleGenerator(schedule=self.schedule)
        return generator.generate_fixtures(shuffle_order=shuffle_order, teams=teams, **kwargs)
