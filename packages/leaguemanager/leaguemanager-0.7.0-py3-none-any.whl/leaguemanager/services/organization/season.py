from typing import Any
from uuid import UUID

from advanced_alchemy.filters import FilterTypes
from attrs import define, field
from sqlalchemy import select

from leaguemanager.models import League, Season
from leaguemanager.repository import SeasonSyncRepository
from leaguemanager.repository._async import SeasonAsyncRepository
from leaguemanager.services.base import SQLAlchemyAsyncRepositoryService, SQLAlchemySyncRepositoryService

__all__ = ["SeasonSyncService", "SeasonAsyncService"]


class SeasonSyncService(SQLAlchemySyncRepositoryService):
    """Handles sync database operations for season data."""

    repository_type = SeasonSyncRepository

    def get_leagues_in_season(self, *filters: FilterTypes, season_id: UUID, **kwargs) -> Season:
        """Get the current season."""

        statement = select(League).join_from(Season, League).where(Season.id == season_id)

        return self.list(*filters, statement=statement, **kwargs)

    def get_active_seasons(self, *filters: FilterTypes, **kwargs) -> Season:
        """Get active seasons."""

        return self.list(*filters, **kwargs | {"active": True})


class SeasonAsyncService(SQLAlchemyAsyncRepositoryService):
    """Handles async database operations for season data."""

    repository_type = SeasonAsyncRepository

    async def get_leagues_in_season(self, *filters: FilterTypes, season_id: UUID, **kwargs) -> Season:
        """Get the current season."""

        statement = select(League).join_from(Season, League).where(Season.id == season_id)

        return await self.list(*filters, statement=statement, **kwargs)

    async def get_active_seasons(self, *filters: FilterTypes, **kwargs) -> Season:
        """Get active seasons."""

        statement = select(Season).where(Season.active == True)  # noqa

        return await self.list(*filters, statement=statement, **kwargs)
