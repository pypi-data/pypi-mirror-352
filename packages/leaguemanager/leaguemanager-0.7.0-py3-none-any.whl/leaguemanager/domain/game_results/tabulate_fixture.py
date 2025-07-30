from attrs import define, field
from sqlalchemy import select
from sqlalchemy.orm import Session

from leaguemanager import models
from leaguemanager.services import FixtureTeamSyncService, StandingsSyncService, TeamSyncService


@define
class TabulateFixture:
    """Updates the stats to the Fixture and FixtureTeam tables, as well as the standings."""

    session: Session
    fixture: models.Fixture

    standings_service: StandingsSyncService = field(init=False)
    fixture_team_service: FixtureTeamSyncService = field(init=False)
    team_service: TeamSyncService = field(init=False)

    def __attrs_post_init__(self):
        self.standings_service = StandingsSyncService(session=self.session)
        self.team_service = TeamSyncService(session=self.session)
        self.fixture_team_service = FixtureTeamSyncService(session=self.session)

    @property
    def home_team(self):
        """Get the current standings for the home team."""
        return self.team_service.get(self.fixture.home_team_id)

    @property
    def away_team(self):
        """Get the current standings for the away team."""
        return self.team_service.get(self.fixture.away_team_id)

    def process_fixture_results(self):
        """Updates the fixture_team tables with the results from the fixture.

        Note: These are currently tailored toward soccer leagues, obtaining 3 points per win and
        1 point per draw.
        """

        home_fixture_team = self.fixture_team_service.get(
            self.fixture.id,
            id_attribute="fixture_id",
            statement=select(models.FixtureTeam).where(models.FixtureTeam.team_id == self.fixture.home_team_id),
        )
        away_fixture_team = self.fixture_team_service.get(
            self.fixture.id,
            id_attribute="fixture_id",
            statement=select(models.FixtureTeam).where(models.FixtureTeam.team_id == self.fixture.away_team_id),
        )

        match self.fixture:
            case fixture if self.fixture.status in ["U", "D"]:
                raise ValueError(f"Invalid fixture status: {fixture.status}")
            case fixture if self.fixture.home_goals > fixture.away_goals:
                home_fixture_team.points = 3
                away_fixture_team.points = 0
                home_fixture_team.result = "W"
                away_fixture_team.result = "L"
            case fixture if self.fixture.home_goals < fixture.away_goals:
                home_fixture_team.points = 0
                away_fixture_team.points = 3
                home_fixture_team.result = "L"
                away_fixture_team.result = "W"
            case fixture if self.fixture.home_goals == fixture.away_goals:
                home_fixture_team.points = 1
                away_fixture_team.points = 1
                home_fixture_team.result = "D"
                away_fixture_team.result = "D"
            case fixture if self.fixture.status in ["P", "F", "A"]:
                home_fixture_team.is_played = True
                away_fixture_team.is_played = True

        home_fixture_team.score_for = self.fixture.home_goals
        home_fixture_team.score_against = self.fixture.away_goals
        away_fixture_team.score_for = self.fixture.away_goals
        away_fixture_team.score_against = self.fixture.home_goals

        home_fixture_team = self.fixture_team_service.update(home_fixture_team, auto_commit=True)
        away_fixture_team = self.fixture_team_service.update(away_fixture_team, auto_commit=True)

        home_standings = self.update_standings(self.home_team, home_fixture_team)
        away_standings = self.update_standings(self.away_team, away_fixture_team)

        return home_standings, away_standings

    def update_standings(self, team: models.Team, fixture_team: models.FixtureTeam):
        """Update the standings for the team.

        Args:
            team (models.Team): The team to update.
            fixture_team (models.FixtureTeam): The fixture_team to update.

        Returns:
            models.Standings: The updated standings.
        """
        _standings = self.standings_service.get(team.id, id_attribute="team_id")

        match fixture_team:
            case fixture_team if fixture_team.fixture_result == "W":
                _standings.games_won += 1
            case fixture_team if fixture_team.fixture_result == "L":
                _standings.games_lost += 1
            case fixture_team if fixture_team.fixture_result == "D":
                _standings.games_drawn += 1

        _standings.games_played += 1
        _standings.score_for += fixture_team.score_for
        _standings.score_against += fixture_team.score_against
        _standings.points += fixture_team.points
        _standings.score_diff = _standings.score_for - _standings.score_against

        return self.standings_service.update(_standings, auto_commit=True)
