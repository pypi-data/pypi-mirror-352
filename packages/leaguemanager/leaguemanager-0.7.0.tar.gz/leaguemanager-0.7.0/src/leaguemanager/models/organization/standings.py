from datetime import UTC, datetime
from uuid import UUID

from attrs import define, field
from sqlalchemy import UUID as _UUID
from sqlalchemy import Column, DateTime, ForeignKey, Integer, Table, UniqueConstraint
from sqlalchemy.ext.associationproxy import AssociationProxy, association_proxy
from sqlalchemy.orm import relationship
from typing_extensions import TYPE_CHECKING

from leaguemanager.models.base import UUIDAuditBase, mapper, metadata

if TYPE_CHECKING:
    from .league import League
    from .season import Season
    from .team import Team


@define(slots=False)
class Standings(UUIDAuditBase):
    """Standings table for a given team. The stats are geared toward soccer leagues."""

    schedule_id: UUID | None = field(default=None)
    team_id: UUID | None = field(default=None)

    games_played: int = field(default=0)
    games_won: int = field(default=0)
    games_drawn: int = field(default=0)
    games_lost: int = field(default=0)
    score_for: int = field(default=0)
    score_against: int = field(default=0)
    score_diff: int = field(default=0)
    points: int = field(default=0)

    # team_name: AssociationProxy[str] | None = association_proxy("team", "name")


# SQLAlchemy Imperative Mapping

standings = Table(
    "standings",
    metadata,
    Column("id", _UUID, primary_key=True),
    Column("schedule_id", _UUID, ForeignKey("schedule.id")),
    Column("team_id", _UUID, ForeignKey("team.id")),
    # UniqueConstraint("id", "schedule_id", "team_id", name="uxstandings"),
    Column("games_played", Integer, nullable=False),
    Column("games_won", Integer, nullable=False),
    Column("games_drawn", Integer, nullable=False),
    Column("games_lost", Integer, nullable=False),
    Column("score_for", Integer, nullable=False),
    Column("score_against", Integer, nullable=False),
    Column("points", Integer, nullable=False),
    Column("score_diff", Integer, nullable=False),
    Column("created_at", DateTime, default=lambda: datetime.now(UTC)),
    Column("updated_at", DateTime, default=lambda: datetime.now(UTC), onupdate=datetime.now(UTC)),
)

# ORM Relationships

mapper.map_imperatively(
    Standings,
    standings,
    properties={
        "schedule": relationship("Schedule", back_populates="team_standings", lazy="selectin"),
        "team": relationship("Team", back_populates="standings"),
    },
)
