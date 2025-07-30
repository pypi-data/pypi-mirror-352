from typing import Any
from uuid import UUID

from advanced_alchemy.filters import FilterTypes
from sqlalchemy import select

from leaguemanager.models import Player
from leaguemanager.repository import PlayerSyncRepository
from leaguemanager.repository._async import PlayerAsyncRepository
from leaguemanager.services.base import SQLAlchemyAsyncRepositoryService, SQLAlchemySyncRepositoryService

__all__ = ["PlayerSyncService", "PlayerAsyncService"]


class PlayerSyncService(SQLAlchemySyncRepositoryService):
    """Handles sync database operations for players."""

    repository_type = PlayerSyncRepository


class PlayerAsyncService(SQLAlchemyAsyncRepositoryService):
    """Handles async database operations for players."""

    repository_type = PlayerAsyncRepository
