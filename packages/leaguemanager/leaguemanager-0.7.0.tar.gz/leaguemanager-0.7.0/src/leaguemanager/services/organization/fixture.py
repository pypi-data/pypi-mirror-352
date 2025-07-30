from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID

from advanced_alchemy.filters import CollectionFilter, OnBeforeAfter
from sqlalchemy import select

# from league_manager.domain.scheduling import ScheduleGenerator
from leaguemanager.models import Fixture, FixtureTeam, Team
from leaguemanager.repository import FixtureSyncRepository, FixtureTeamSyncRepository
from leaguemanager.repository._async import FixtureAsyncRepository, FixtureTeamAsyncRepository
from leaguemanager.services._typing import ModelT
from leaguemanager.services.base import SQLAlchemyAsyncRepositoryService, SQLAlchemySyncRepositoryService

__all__ = [
    "FixtureSyncService",
    "FixtureTeamSyncService",
    "FixtureAsyncService",
    "FixtureTeamAsyncService",
]


class FixtureSyncService(SQLAlchemySyncRepositoryService):
    """Handles sync database operations for fixtures."""

    repository_type = FixtureSyncRepository

    def all_fixtures_in_schedule(self, schedule_id: UUID) -> list[Fixture]:
        statement = select(self.model_type).where(self.model_type.schedule_id == schedule_id)
        return self.list(statement=statement)

    def past_fixtures(self, schedule_id: UUID) -> list[Fixture]:
        filter = CollectionFilter(field_name="status", values=["P", "F", "A"])
        statement = select(self.model_type).where((self.model_type.schedule_id == schedule_id))
        return self.list(filter, statement=statement)

    def remaining_fixtures(self, schedule_id: UUID) -> list[Fixture]:
        filter = CollectionFilter(field_name="status", values=["U", "D"])
        statement = select(self.model_type).where((self.model_type.schedule_id == schedule_id))
        return self.list(filter, statement=statement)

    def next_scheduled_fixtures(
        self, schedule_id: UUID, *, days: int = 6, filter: OnBeforeAfter | None = None
    ) -> list[Fixture]:
        if filter is None:
            filter = OnBeforeAfter(
                field_name="date",
                on_or_after=datetime.now(UTC),
                on_or_before=datetime.now(UTC) + timedelta(days=days),
            )
        statement = select(self.model_type).where((self.model_type.schedule_id == schedule_id))
        return self.list(filter, statement=statement)


class FixtureTeamSyncService(SQLAlchemySyncRepositoryService):
    """Handles sync database operations for fixture_team association data."""

    repository_type = FixtureTeamSyncRepository


class FixtureAsyncService(SQLAlchemyAsyncRepositoryService):
    """Handles async database operations for fixtures."""

    repository_type = FixtureAsyncRepository


class FixtureTeamAsyncService(SQLAlchemyAsyncRepositoryService):
    """Handles async database operations for fixture_team association data."""

    repository_type = FixtureTeamAsyncRepository
