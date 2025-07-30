from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any
from uuid import UUID, uuid4

from attrs import define, field
from sqlalchemy import MetaData
from sqlalchemy.orm import Mapper, registry

mapper = registry()
metadata = MetaData()


@define(slots=False)
class UUIDBase:
    id: UUID = field(factory=uuid4)

    if TYPE_CHECKING:
        __name__: str
        __mapper__: Mapper[Any]

    def to_dict(self, exclude: set[str] | None = None) -> dict[str, Any]:
        """Convert model to dictionary.

        Returns:
            Dict[str, Any]: A dict representation of the model
        """
        exclude = {"sa_orm_sentinel", "_sentinel"}.union(self._sa_instance_state.unloaded).union(exclude or [])  # type: ignore[attr-defined]
        return {
            field: getattr(self, field)
            for field in self.__mapper__.columns.keys()  # noqa: SIM118
            if field not in exclude
        }

    def str_to_iso(date_string: str, format: str):
        """Converts string to datetime object."""
        return datetime.strptime(date_string, format)


@define(slots=False)
class UUIDAuditBase(UUIDBase):
    created_at: datetime = field(factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(factory=lambda: datetime.now(UTC))
