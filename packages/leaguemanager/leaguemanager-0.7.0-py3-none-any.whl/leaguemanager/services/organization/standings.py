from typing import Any
from uuid import UUID

from advanced_alchemy.filters import FilterTypes
from sqlalchemy import select

from leaguemanager.models import Standings, Team
from leaguemanager.repository import StandingsSyncRepository
from leaguemanager.repository._async import StandingsAsyncRepository
from leaguemanager.services.base import SQLAlchemyAsyncRepositoryService, SQLAlchemySyncRepositoryService

__all__ = ["StandingsSyncService", "StandingsAsyncService"]


class StandingsSyncService(SQLAlchemySyncRepositoryService):
    """Handles sync database operations for standings."""

    repository_type = StandingsSyncRepository


class StandingsAsyncService(SQLAlchemyAsyncRepositoryService):
    """Handles async database operations for standings."""

    repository_type = StandingsAsyncRepository
