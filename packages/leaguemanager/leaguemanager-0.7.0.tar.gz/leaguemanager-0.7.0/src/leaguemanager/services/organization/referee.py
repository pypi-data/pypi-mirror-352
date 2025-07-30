from typing import Any
from uuid import UUID

from advanced_alchemy.filters import FilterTypes
from attrs import define, field
from sqlalchemy import select

from leaguemanager.models import Referee, User
from leaguemanager.repository import RefereeSyncRepository
from leaguemanager.repository._async import RefereeAsyncRepository
from leaguemanager.services.base import SQLAlchemyAsyncRepositoryService, SQLAlchemySyncRepositoryService

__all__ = ["RefereeSyncService", "RefereeAsyncService"]


class RefereeSyncService(SQLAlchemySyncRepositoryService):
    """Handles sync database operations for referees."""

    repository_type = RefereeSyncRepository


class RefereeAsyncService(SQLAlchemyAsyncRepositoryService):
    """Handles async database operations for referees."""

    repository_type = RefereeAsyncRepository
