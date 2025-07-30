from typing import Any
from uuid import UUID

from advanced_alchemy.filters import FilterTypes
from sqlalchemy import select

from leaguemanager.models import League, Team
from leaguemanager.repository import TeamSyncRepository
from leaguemanager.repository._async import TeamAsyncRepository
from leaguemanager.services.base import SQLAlchemyAsyncRepositoryService, SQLAlchemySyncRepositoryService

__all__ = ["TeamSyncService", "TeamAsyncService"]


class TeamSyncService(SQLAlchemySyncRepositoryService):
    """Handles sync database operations for team data."""

    repository_type = TeamSyncRepository


class TeamAsyncService(SQLAlchemyAsyncRepositoryService):
    """Handles async database operations for team data."""

    repository_type = TeamAsyncRepository
