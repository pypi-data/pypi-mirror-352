from datetime import UTC, datetime
from uuid import UUID

from attrs import define, field, validators
from sqlalchemy import UUID as SA_UUID
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Table, UniqueConstraint
from sqlalchemy.ext.associationproxy import AssociationProxy, association_proxy
from sqlalchemy.orm import relationship
from typing_extensions import TYPE_CHECKING

from leaguemanager.models.base import UUIDAuditBase, mapper, metadata
from leaguemanager.models.enums import Category, Division, MatchDay

if TYPE_CHECKING:
    from .schedule import Schedule
    from .season import Season
    from .team import Team


@define(slots=False)
class League(UUIDAuditBase):
    """Defines a Generic League linked to a specific Ruleset."""

    season_id: UUID | None = field(default=None)

    active: bool = field(default=True)

    name: str | None = field(default=None, validator=validators.max_len(80))
    description: str | None = field(default=None, validator=validators.optional(validators.max_len(255)))

    sport: str | None = field(default=None, validator=validators.optional(validators.max_len(80)))


# SQLAlchemy Imperative Mapping

league = Table(
    "league",
    metadata,
    Column("id", SA_UUID, primary_key=True),
    Column("season_id", SA_UUID, ForeignKey("season.id")),
    Column("active", Boolean, default=True),
    Column("name", String(80), nullable=False, unique=True),
    Column("description", String(255), nullable=True),
    Column("sport", String(80), nullable=True),
    Column("created_at", DateTime, default=lambda: datetime.now(UTC)),
    Column("updated_at", DateTime, default=lambda: datetime.now(UTC), onupdate=datetime.now(UTC)),
)

# ORM Relationships

mapper.map_imperatively(
    League,
    league,
    properties={
        "ruleset": relationship(
            "Ruleset",
            back_populates="leagues",
            uselist=False,
            lazy="selectin",
        ),
        "season": relationship("Season", back_populates="leagues", lazy="selectin"),
        "schedule": relationship("Schedule", back_populates="league", uselist=False, lazy="selectin"),
        "teams": relationship("Team", back_populates="league", lazy="selectin"),
    },
)
