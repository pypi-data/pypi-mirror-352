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

from ._association import player_team

if TYPE_CHECKING:
    from ..account.user import User
    from .team import Team


@define(slots=False)
class Player(UUIDAuditBase):
    """A player in a team."""

    first_name: str | None = field(default=None, validator=validators.max_len(40))
    last_name: str | None = field(default=None, validator=validators.max_len(40))
    age_verified: bool = field(default=False)
    age: int | None = field(default=None)
    gender: str | None = field(default=None, validator=validators.optional(validators.in_([v.name for v in Gender])))
    note: str | None = field(default=None, validator=validators.optional(validators.max_len(255)))


# SQLAlchemy Imperative Mappings

player = Table(
    "player",
    metadata,
    Column("id", _UUID, primary_key=True),
    Column("first_name", String(40), nullable=False),
    Column("last_name", String(40), nullable=False),
    Column("age", Integer),
    Column("age_verified", Boolean),
    Column(
        "gender",
        String(2),
    ),
    Column("note", String(255)),
    Column("user_profile_id", _UUID, ForeignKey("user.id")),
    Column("created_at", DateTime, default=lambda: datetime.now(UTC)),
    Column("updated_at", DateTime, default=lambda: datetime.now(UTC), onupdate=datetime.now(UTC)),
)

# ORM Relationships

mapper.map_imperatively(
    Player,
    player,
    properties={
        "user": relationship("User", back_populates="player"),
        "teams": relationship("Team", secondary=player_team, back_populates="players"),
    },
)
