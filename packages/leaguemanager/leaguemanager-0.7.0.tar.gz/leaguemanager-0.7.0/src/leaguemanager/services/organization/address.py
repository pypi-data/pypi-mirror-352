from advanced_alchemy.filters import FilterTypes

from leaguemanager.models import Address, City, Country, State
from leaguemanager.repository import (
    AddressSyncRepository,
    CitySyncRepository,
    CountrySyncRepository,
    StateSyncRepository,
)
from leaguemanager.repository._async import (
    AddressAsyncRepository,
    CityAsyncRepository,
    CountryAsyncRepository,
    StateAsyncRepository,
)
from leaguemanager.services.base import SQLAlchemyAsyncRepositoryService, SQLAlchemySyncRepositoryService

__all__ = ["AddressSyncService", "AddressAsyncService"]


class AddressSyncService(SQLAlchemySyncRepositoryService):
    """Handles sync database operations for standings."""

    repository_type = AddressSyncRepository


class AddressAsyncService(SQLAlchemyAsyncRepositoryService):
    """Handles async database operations for standings."""

    repository_type = AddressAsyncRepository


class CitySyncService(SQLAlchemySyncRepositoryService):
    """Handles sync database operations for cities."""

    repository_type = CitySyncRepository


class CityAsyncService(SQLAlchemyAsyncRepositoryService):
    """Handles async database operations for cities."""

    repository_type = CityAsyncRepository


class CountrySyncService(SQLAlchemySyncRepositoryService):
    """Handles sync database operations for countries."""

    repository_type = CountrySyncRepository


class CountryAsyncService(SQLAlchemyAsyncRepositoryService):
    """Handles async database operations for countries."""

    repository_type = CountryAsyncRepository


class StateSyncService(SQLAlchemySyncRepositoryService):
    """Handles sync database operations for states."""

    repository_type = StateSyncRepository


class StateAsyncService(SQLAlchemyAsyncRepositoryService):
    """Handles async database operations for states."""

    repository_type = StateAsyncRepository
