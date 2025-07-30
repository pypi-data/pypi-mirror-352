from typing import Any
from uuid import UUID

from advanced_alchemy.filters import FilterTypes
from sqlalchemy import select

from leaguemanager.models import Schedule, Season, Team
from leaguemanager.repository import ScheduleSyncRepository
from leaguemanager.repository._async import ScheduleAsyncRepository
from leaguemanager.services.base import SQLAlchemyAsyncRepositoryService, SQLAlchemySyncRepositoryService

__all__ = ["ScheduleSyncService", "ScheduleAsyncService"]


class ScheduleSyncService(SQLAlchemySyncRepositoryService):
    """Handles sync database operations for scheduling."""

    repository_type = ScheduleSyncRepository


class ScheduleAsyncService(SQLAlchemyAsyncRepositoryService):
    """Handles async database operations for scheduling."""

    repository_type = ScheduleAsyncRepository
