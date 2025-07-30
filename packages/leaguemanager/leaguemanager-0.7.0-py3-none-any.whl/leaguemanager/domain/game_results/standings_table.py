from advanced_alchemy.filters import CollectionFilter, OrderBy
from attrs import define, field
from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from leaguemanager import models
from leaguemanager.services import (
    FixtureSyncService,
    FixtureTeamSyncService,
    StandingsSyncService,
    TeamSyncService,
)


@define
class StandingsTable:
    """Responsible for creating and updating the standings table for a schedule."""

    session: Session
    schedule: models.Schedule

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

    def get_or_create_current_standings(self):
        """Get or create the current standings for the schedule.

        If the schedule does not have any team standings, we create them.

        Returns:
            Sequence[models.Standings]: All standings (per team) for the schedule
        """
        if not self.schedule.team_standings:
            standings = []
            for team in self.schedule.league.teams:
                standings.append(
                    models.Standings(
                        schedule_id=self.schedule.id,
                        team_id=team.id,
                    )
                )
            standings = self.standings_service.create_many(standings)
            return standings
        return self.schedule.team_standings

    def link_teams_to_fixtures(self):
        """Link all fixtures for the schedule to their teams.

        This is done through an association table (fixture_team). For each fixture,
        we create two fixture_team rows, one for the home team and one for the away team.

        Raises:
            NoResultFound: In the event that no fixtures are found, we raise an exception

        Returns:
            Sequence[models.FixtureTeam]: List of association tables (fixture_team) with fixture data.
        """
        all_fixtures = self.fixture_service.all_fixtures_in_schedule(self.schedule.id)

        if not all_fixtures:
            raise NoResultFound(f"No fixtures found for {self.schedule}")

        for fixture in all_fixtures:
            home_fixture_team = models.FixtureTeam(
                fixture_id=fixture.id,
                team_id=fixture.home_team_id,
            )
            self.fixture_team_service.create(home_fixture_team)

            away_fixture_team = models.FixtureTeam(
                fixture_id=fixture.id,
                team_id=fixture.away_team_id,
            )
            self.fixture_team_service.create(away_fixture_team)

        return self.fixture_team_service.list()

    @property
    def teams(self):
        return self.schedule.league.teams

    @property
    def all_fixtures(self):
        """List of all fixtures in the schedule."""
        return self.fixture_service.all_fixtures_in_schedule(self.schedule.id)

    @property
    def past_fixtures(self):
        """List of fixtures that have already been played."""
        return self.fixture_service.past_fixtures(self.schedule.id)

    @property
    def remaining_fixtures(self):
        """List of fixtures that have not yet been played."""
        return self.fixture_service.remaining_fixtures(self.schedule.id)

    def next_scheduled_fixtures(self, days: int = 6, **kwargs):
        return self.fixture_service.next_scheduled_fixtures(self.schedule.id, days=days, **kwargs)

    def generate_standings_table(self, order_by_field: str = "points", sort_order: str = "desc"):
        """Retrieve standings for all teams.

        The order defaults to descending by points (first in order has most points), although
        any field can be used. In case of a tie, the order is by goals difference. (The highest
        goals difference is ordered first.)

        Args:
            order_by_field (str, optional): Field to order by. Defaults to "points".
            sort_order (str, optional): Either "asc" or "desc". Defaults to "desc".

        Returns:
            Sequence[models.Standings]: Standings table for all teams
        """

        standings = self.standings_service.list(
            CollectionFilter(field_name="team_id", values=[team.id for team in self.teams]),
            OrderBy(field_name=order_by_field, sort_order=sort_order),
            OrderBy(field_name="score_diff", sort_order="desc"),
            statement=select(models.Standings).where(models.Standings.schedule_id == self.schedule.id),
        )
        return standings
