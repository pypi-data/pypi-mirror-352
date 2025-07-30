from datetime import UTC, datetime
from uuid import UUID

from attrs import define, field, validators
from sqlalchemy import UUID as _UUID
from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, String, Table
from sqlalchemy.ext.associationproxy import AssociationProxy, association_proxy
from sqlalchemy.orm import relationship
from typing_extensions import TYPE_CHECKING

from leaguemanager.models.base import UUIDAuditBase, mapper, metadata

from ._association import fixture_referee

if TYPE_CHECKING:
    from .user import User


@define(slots=False)
class Referee(UUIDAuditBase):
    """A referee for a fixture."""

    user_id: UUID | None = field(default=None)
    fixture_id: UUID | None = field(default=None)
    verified: bool = field(default=False)
    first_name: str | None = field(default=None, validator=validators.max_len(40))
    last_name: str | None = field(default=None, validator=validators.max_len(40))
    note: str | None = field(default=None, validator=validators.optional(validators.max_len(255)))
    license: str | None = field(default=None, validator=validators.max_len(20))
    price_per_game: float | None = field(default=None)

    user_email: AssociationProxy[str] = association_proxy("user", "email")


# SQLalchemy Imperative Mapping

referee = Table(
    "referee",
    metadata,
    Column("id", _UUID, primary_key=True),
    Column("user_id", _UUID, ForeignKey("user.id")),
    Column("fixture_id", _UUID, ForeignKey("fixture.id")),
    Column("first_name", String(40)),
    Column("last_name", String(40)),
    Column("note", String(255)),
    Column("license", String(20)),
    Column("verified", Boolean),
    Column("price_per_game", Float),
    Column("created_at", DateTime, default=lambda: datetime.now(UTC)),
    Column("updated_at", DateTime, default=lambda: datetime.now(UTC), onupdate=datetime.now(UTC)),
)

# ORM Relationships

mapper.map_imperatively(
    Referee,
    referee,
    properties={
        "user": relationship("User", back_populates="referee", uselist=False),
        "fixtures": relationship("Fixture", secondary=fixture_referee, back_populates="referees"),
    },
)
