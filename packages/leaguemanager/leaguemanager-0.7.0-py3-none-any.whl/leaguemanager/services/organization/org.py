from advanced_alchemy.filters import FilterTypes

from leaguemanager.models import Organization
from leaguemanager.repository import OrganizationSyncRepository
from leaguemanager.repository._async import OrganizationAsyncRepository
from leaguemanager.services.base import SQLAlchemyAsyncRepositoryService, SQLAlchemySyncRepositoryService

__all__ = ["OrganizationSyncService", "OrganizationAsyncService"]


class OrganizationSyncService(SQLAlchemySyncRepositoryService):
    """Handles sync database operations for standings."""

    repository_type = OrganizationSyncRepository


class OrganizationAsyncService(SQLAlchemyAsyncRepositoryService):
    """Handles async database operations for standings."""

    repository_type = OrganizationAsyncRepository
