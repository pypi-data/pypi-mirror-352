from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from attrs import define, field, validators
from sqlalchemy import UUID as _UUID
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, Table
from sqlalchemy.ext.associationproxy import AssociationProxy, association_proxy
from sqlalchemy.orm import relationship
from typing_extensions import TYPE_CHECKING

from leaguemanager.models.base import UUIDAuditBase, mapper, metadata

from ._association import player_team

if TYPE_CHECKING:
    from ..account.user import User
    from .league import League
    from .player import Player
    from .standings import Standings


@define(slots=False)
class Team(UUIDAuditBase):
    """A team belonging to a specific league."""

    manager_id: UUID | None = field(default=None)
    league_id: UUID | None = field(default=None)
    active: bool = field(default=True)

    name: str | None = field(default=None, validator=validators.max_len(80))
    color_main: str | None = field(default=None, validator=validators.optional(validators.max_len(20)))
    color_secondary: str | None = field(default=None, validator=validators.optional(validators.max_len(20)))
    team_image: str | None = field(default=None)
    team_logo: str | None = field(default=None)

    # player_ids: list[AssociationProxy[str]] | None = association_proxy("players", "first_name")


# SQLAlchemy Imperative Mapping

team = Table(
    "team",
    metadata,
    Column("id", _UUID, primary_key=True),
    Column("manager_id", _UUID, ForeignKey("manager.id")),
    Column("league_id", _UUID, ForeignKey("league.id")),
    Column("name", String(80), nullable=False),
    Column("color_main", String(20)),
    Column("color_secondary", String(20)),
    Column("active", Boolean),
    Column("team_image", String(255)),
    Column("team_logo", String(255)),
    Column("created_at", DateTime, default=lambda: datetime.now(UTC)),
    Column("updated_at", DateTime, default=lambda: datetime.now(UTC), onupdate=datetime.now(UTC)),
)

# ORM Relationships

mapper.map_imperatively(
    Team,
    team,
    properties={
        "manager": relationship("Manager", back_populates="teams"),
        "league": relationship("League", back_populates="teams"),
        "players": relationship("Player", secondary=player_team, back_populates="teams"),
        "standings": relationship("Standings", back_populates="team"),
        "fixtures": relationship("FixtureTeam", back_populates="team"),
    },
)
