from __future__ import annotations

import typer
from sqlalchemy.orm import Session

from leaguemanager.dependency import LeagueManager
from leaguemanager.services._typing import SQLAlchemyAsyncConfigT, SQLAlchemySyncConfigT, SyncRepositoryT, SyncServiceT

registry = LeagueManager()


def provide_manager_service(param: typer.CallbackParam) -> SyncServiceT | SyncRepositoryT:
    return registry.provide_db_service(service_type=param.type.func)


def provide_manager_repository(param: typer.CallbackParam) -> SyncRepositoryT:
    return registry.provide_db_repository(repository_type=param.type.func)


def provide_sync_db_session() -> Session:
    return registry.provide_db_session


def provide_sync_db_config() -> SQLAlchemySyncConfigT:
    return registry.provide_sync_config


def provide_async_db_config() -> SQLAlchemyAsyncConfigT:
    return registry.provide_async_config
