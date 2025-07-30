from datetime import UTC, datetime
from uuid import UUID

from attrs import define, field, validators
from sqlalchemy import UUID as _UUID
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Table
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship
from typing_extensions import TYPE_CHECKING

from leaguemanager.models.base import UUIDAuditBase, mapper, metadata
from leaguemanager.models.enums import Gender

if TYPE_CHECKING:
    from .team import Team
    from .user import User


@define(slots=False)
class Manager(UUIDAuditBase):
    """A manager of a team."""

    user_id: UUID | None = field(default=None)
    first_name: str | None = field(default=None, validator=validators.max_len(40))
    last_name: str | None = field(default=None, validator=validators.max_len(40))
    verified: bool = field(default=True)
    phone_number: str | None = field(default=None, validator=validators.max_len(20))
    team_email: str | None = field(default=None, validator=validators.max_len(40))
    note: str | None = field(default=None, validator=validators.optional(validators.max_len(255)))


# SQLAlchemy Imperative Mappings

manager = Table(
    "manager",
    metadata,
    Column("id", _UUID, primary_key=True),
    Column("user_id", _UUID, ForeignKey("user.id")),
    Column("first_name", String(40), nullable=False),
    Column("last_name", String(40), nullable=False),
    Column("verified", Boolean),
    Column("phone_number", String(20)),
    Column("team_email", String(40)),
    Column("note", String(255)),
    Column("created_at", DateTime, default=lambda: datetime.now(UTC)),
    Column("updated_at", DateTime, default=lambda: datetime.now(UTC), onupdate=datetime.now(UTC)),
)

# ORM Relationships

mapper.map_imperatively(
    Manager,
    manager,
    properties={
        "user": relationship("User", back_populates="manager"),
        "teams": relationship("Team", back_populates="manager"),
    },
)
