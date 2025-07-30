from typing import Any
from uuid import UUID

from advanced_alchemy.filters import FilterTypes
from sqlalchemy import select

from leaguemanager.models import League, Season
from leaguemanager.repository import LeagueSyncRepository
from leaguemanager.repository._async import LeagueAsyncRepository
from leaguemanager.services.base import SQLAlchemyAsyncRepositoryService, SQLAlchemySyncRepositoryService

__all__ = ["LeagueSyncService", "LeagueAsyncService"]


class LeagueSyncService(SQLAlchemySyncRepositoryService):
    """Handles sync database operations for a league."""

    repository_type = LeagueSyncRepository

    def get_active_leagues(self, *filters: FilterTypes, **kwargs) -> League:
        """Get active leagues."""

        statement = select(League).where(League.active == True)  # noqa

        return self.list(*filters, statement=statement, **kwargs)

    def get_leagues_in_season(self, *filters: FilterTypes, season_id: UUID, **kwargs) -> Season:
        """Get the current season."""

        statement = select(League).join_from(Season, League).where(Season.id == season_id)

        return self.list(*filters, statement=statement, **kwargs)


class LeagueAsyncService(SQLAlchemyAsyncRepositoryService):
    """Handles async database operations for a league."""

    repository_type = LeagueAsyncRepository

    async def get_active_leagues(self, *filters: FilterTypes, **kwargs) -> League:
        """Get active leagues."""

        statement = select(League).where(League.active == True)  # noqa

        return await self.list(*filters, statement=statement, **kwargs)
