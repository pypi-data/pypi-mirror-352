import datetime
from collections import deque
from itertools import chain
from random import shuffle
from typing import Any, Iterable

from attrs import define

from leaguemanager.models import Fixture, Schedule, Team
from leaguemanager.models.enums import Field

__all__ = ["ScheduleGenerator"]


@define
class ScheduleGenerator:
    """Schedules fixtures(matches) based on the league configuration."""

    schedule: Schedule
    blackout_dates: list[datetime.datetime] | None = None  # TODO: Implement with days or ranges?

    @property
    def total_games(self) -> int:
        return self.schedule.total_games

    @property
    def teams(self) -> list[Team]:
        try:
            return self.schedule.league.teams
        except AttributeError:
            raise ValueError("The league does not have any teams associated.") from AttributeError

    def split_teams(self, teams: Iterable[Team]) -> tuple[list[Team], list[Team]]:
        """Split a list of teams in half, raising an error if the list is odd."""

        if len(teams) % 2 != 0:
            raise ValueError("List length must be even.")

        return (
            teams[: len(teams) // 2],
            teams[len(teams) // 2 :],
        )

    def determine_field(self, match_count: int, concurrent_games: int | None = None) -> str:
        fields = [f.name for f in Field]
        if not concurrent_games:
            concurrent_games = self.schedule.concurrent_games
        if match_count == 1 or match_count > concurrent_games:
            return fields[0]
        return fields[match_count - 1]

    def home_or_away(self, round_number: int, match: tuple[Team, Team]) -> tuple[Team, Team]:
        if round_number % 2 == 0:
            home_team, away_team = match
        else:
            home_team, away_team = match[::-1]

        return home_team, away_team

    def check_for_bye(self, match: tuple[Team, Team]) -> bool:
        if match[0].name == "Bye Week" or match[1].name == "Bye Week":
            return True
        return False

    def increment_matchday(self, matchday: int, *, increment_by_days: int = 7) -> None:
        matchday_start_time = self.schedule.start_date
        if matchday > 1:
            matchday_start_time += datetime.timedelta(days=increment_by_days * (matchday - 1))
        return matchday_start_time

    def determine_start_time(self, matchday: int, match_count: int) -> datetime.datetime:
        game_date = self.increment_matchday(matchday)

        if match_count <= self.schedule.concurrent_games:
            return game_date
        increment_by = self.schedule.game_length + self.schedule.half_time + self.schedule.time_between_games
        multiplier = (match_count - 1) // self.schedule.concurrent_games
        minute_increment = increment_by * (multiplier)
        return game_date + datetime.timedelta(minutes=minute_increment)

    def create_matchups(self, matchday: int, teams: list[Team] | None = None) -> list[tuple[Team]]:
        """Creates matchups by rotating teams based on the matchday.

        See: https://en.wikipedia.org/wiki/Round-robin_tournament#Circle_method for
        details on round-robin scheduling. In order to account for "odd" number of teams,
        we add a temporary "bye week" team to the list of teams, anchoring the first team
        for rotation.

        Args:
            matchday (int): Current matchday
            teams (list[Team]) | None: List of teams. Defaults to self.teams

        Returns:
            matchups (list[tuple[Team]]): List of tuples corresponding to matchups
        """
        if not teams:
            teams = self.teams
        if len(teams) % 2 != 0:
            teams.append(Team(name="Bye Week"))
        home, away = self.split_teams(teams)
        matchups = list(zip(home, away, strict=True))
        if not matchday == 1:
            _teams = deque(chain(*matchups))
            anchor = _teams.popleft()
            _teams.rotate(matchday)
            _teams.appendleft(anchor)
            home, away = self.split_teams([*_teams])
            matchups = list(zip(home, away, strict=True))
        return matchups

    def create_matchday_fixtures(
        self, matchday: int, round_number: int, teams: list[Team] | None = None
    ) -> list[Fixture]:
        """Creates fixtures for a single matchday.

        Args:
            matchday (int): Current matchday
            round_number (int): Current round number
            teams (list[Team]) | None: List of teams. Defaults to self.teams

        Returns:
            fixtures (list[Fixture]): List of fixtures

        """
        fixtures = []
        matchups = self.create_matchups(matchday, teams)

        for match_count, match in enumerate(matchups, start=1):
            home, away = self.home_or_away(round_number=round_number, match=match)
            start_time = self.determine_start_time(matchday=matchday, match_count=match_count)
            field = self.determine_field(match_count=match_count)

            fixture = Fixture(
                schedule_id=self.schedule.id,
                season_id=self.schedule.season_id,
                league_id=self.schedule.league_id,
                home_team_id=home.id,
                away_team_id=away.id,
                bye_week=self.check_for_bye(match),
                matchday=matchday,
                date=start_time,
                field=field,
            )

            fixtures.append(fixture)

        return fixtures

    def generate_fixtures(self, shuffle_order: bool = True, teams: list[Team] | None = None, **kwargs) -> list[Any]:
        """Generates fixtures for the entire season."""
        if not teams:
            teams = self.teams
        if self.schedule.fixtures:
            raise ValueError("Schedule already has fixtures...")
        all_fixtures = []
        if shuffle_order:
            shuffle(teams)

        # Calculates number of full rounds, and remaining games (if any) left in the schedule
        rounds, remaining = divmod(self.total_games, len(teams))

        if rounds == 0:
            raise ValueError("Not enough matchdays for all teams to play each other.")

        for matchday in range(1, (self.total_games - remaining) + 1):
            round_number = matchday // (len(teams))
            round_number += 1
            matchday_fixtures = self.create_matchday_fixtures(matchday, round_number, teams)
            all_fixtures.extend(matchday_fixtures)

        return all_fixtures

    def generate_tournament_fixtures(self) -> None:
        raise NotImplementedError("Not implemented yet")
