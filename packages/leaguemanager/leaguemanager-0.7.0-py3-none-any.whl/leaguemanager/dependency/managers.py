from __future__ import annotations

from typing import Iterator

from attrs import define, field
from sqlalchemy import select
from sqlalchemy.orm import Session

from leaguemanager.services._typing import AsyncRepositoryT, AsyncServiceT, ModelT, SyncRepositoryT, SyncServiceT

__all__ = ["ServiceManagement", "RepositoryManagement"]


@define
class ServiceManagement:
    """Manages a SQLAlchemySyncRepositoryService[ModelT] class.

    TODO: Async support

    Given the `service_type` and `db_session`, as well as a db_session, it will hold then provide
    the applicable service (for the corresponding service type.). The `get_service` property will
    return the appropriate service for the given `service_type` and `db_session`.

    Attributes:
        service_type (type[SyncServiceT] | type[AsyncServiceT]): Service type to manage.
        model_type (type[ModelT]): Model type for the given `service_type`.
        db_session (Session | None): Database session to use for the service.

    Example:
      >>> _service = ServiceManagement(
      ...     service_type=SeasonSyncService, model_type=Season, db_session=session
      ... )
      >>> _service.get_service
    """

    service_type: type[SyncServiceT] = field()
    model_type: type[ModelT] = field(init=False)
    db_session: Session = field(default=None)

    def __attrs_post_init__(self):
        self.model_type = self.service_type.repository_type.model_type

    @property
    def get_service(self) -> Iterator[ServiceManagement.service_type]:
        with self.service_type.new(session=self.db_session, statement=select(self.model_type)) as service:
            yield service


@define
class RepositoryManagement:
    """Manages a SQLAlchemySyncRepository class.

    TODO: Async support

    Given the `repository_type` as well as a db_session, it will hold then provide
    the applicable repository (for the corresponding repository type.). The `get_repository` property will
    return the appropriate repository for the given `repository_type` and `db_session`.

    Attributes:
        repository_type (type[SyncRepositoryT] | type[AsyncRepositoryT]): Repository type to manage.
        db_session (Session | None): Database session to use for the repository.

    Example:
      >>> _repository = RepositoryManagement(
      ...     repository_type=SeasonSyncRepository, db_session=session
      ... )
      >>> _repository.get_repository
    """

    repository_type: type[SyncRepositoryT] = field()
    db_session: Session = field(default=None)

    @property
    def get_repository(self) -> Iterator[RepositoryManagement.repository_type]:
        return self.repository_type(session=self.db_session, statement=select(self.repository_type.model_type))
