from typing import Any
from uuid import UUID

from advanced_alchemy.filters import FilterTypes
from sqlalchemy import select

from leaguemanager.models import Ruleset, Standings, Team
from leaguemanager.repository import RulesetSyncRepository
from leaguemanager.repository._async import RulesetAsyncRepository
from leaguemanager.services.base import SQLAlchemyAsyncRepositoryService, SQLAlchemySyncRepositoryService

__all__ = ["RulesetSyncService", "RulesetAsyncService"]


class RulesetSyncService(SQLAlchemySyncRepositoryService):
    """Handles sync database operations for standings."""

    repository_type = RulesetSyncRepository


class RulesetAsyncService(SQLAlchemyAsyncRepositoryService):
    """Handles async database operations for standings."""

    repository_type = RulesetAsyncRepository
