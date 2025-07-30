from __future__ import annotations

from typing import TYPE_CHECKING, TypeVar

from advanced_alchemy.config import SQLAlchemyAsyncConfig, SQLAlchemySyncConfig
from advanced_alchemy.repository import SQLAlchemyAsyncRepository, SQLAlchemySyncRepository
from advanced_alchemy.service import SQLAlchemyAsyncRepositoryService, SQLAlchemySyncRepositoryService

from leaguemanager.models.base import UUIDBase

ModelT = TypeVar("ModelT", bound=UUIDBase)
SyncRepositoryT = TypeVar("RepositoryT", bound=SQLAlchemySyncRepository)
AsyncRepositoryT = TypeVar("RepositoryT", bound=SQLAlchemyAsyncRepository)
SyncServiceT = TypeVar("ServiceT", bound=SQLAlchemySyncRepositoryService[ModelT])
AsyncServiceT = TypeVar("ServiceT", bound=SQLAlchemyAsyncRepositoryService[ModelT])
SQLAlchemySyncConfigT = TypeVar("ConfigT", bound=SQLAlchemySyncConfig)
SQLAlchemyAsyncConfigT = TypeVar("ConfigT", bound=SQLAlchemyAsyncConfig)
