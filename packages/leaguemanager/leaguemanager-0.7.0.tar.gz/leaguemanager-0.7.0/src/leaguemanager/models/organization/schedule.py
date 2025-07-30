from datetime import UTC, datetime
from uuid import UUID

from attrs import define, field, validators
from sqlalchemy import UUID as _UUID
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Table, UniqueConstraint
from sqlalchemy.ext.associationproxy import AssociationProxy, association_proxy
from sqlalchemy.orm import relationship
from typing_extensions import TYPE_CHECKING

from leaguemanager.core import get_settings, toolbox
from leaguemanager.models.base import UUIDAuditBase, mapper, metadata

if TYPE_CHECKING:
    from .fixture import Fixture
    from .league import League
    from .season import Season

settings = get_settings()


@define(slots=False)
class Schedule(UUIDAuditBase):
    """Defines the schedule for a league and rules for fixtures."""

    league_id: UUID | None = field(default=None)
    season_id: UUID | None = field(default=None)
    name: str | None = field(default=None, validator=validators.optional(validators.max_len(80)))
    total_games: int = field(default=10)
    game_length: int = field(default=90)
    half_time: int = field(default=15)
    time_between_games: int = field(default=15)
    concurrent_games: int = field(default=2)
    start_date: datetime | None = field(default=None, converter=lambda x: toolbox.str_to_iso(x, settings.DATE_FORMAT))
    end_date: datetime | None = field(default=None)
    active: bool = field(default=True)

    # season_name: AssociationProxy[str] = association_proxy("season", "name")


# SQLAlchemy Imperative Mappings

schedule = Table(
    "schedule",
    metadata,
    Column("id", _UUID, primary_key=True),
    Column("league_id", _UUID, ForeignKey("league.id"), nullable=True),
    Column("season_id", _UUID, ForeignKey("season.id"), nullable=True),
    UniqueConstraint("id", "league_id", "season_id", name="uxschedule"),
    Column("name", String(80), nullable=True),
    Column("total_games", Integer, nullable=False),
    Column("game_length", Integer, nullable=False),
    Column("half_time", Integer, nullable=False),
    Column("time_between_games", Integer, nullable=False),
    Column("concurrent_games", Integer, nullable=False),
    Column("start_date", DateTime(20), nullable=True),
    Column("end_date", DateTime(20), nullable=True),
    Column("active", Boolean, nullable=False),
    Column("created_at", DateTime, default=lambda: datetime.now(UTC)),
    Column("updated_at", DateTime, default=lambda: datetime.now(UTC), onupdate=datetime.now(UTC)),
)

# ORM Relationships

mapper.map_imperatively(
    Schedule,
    schedule,
    properties={
        "league": relationship("League", back_populates="schedule", innerjoin=True, uselist=False, lazy="joined"),
        "season": relationship("Season", back_populates="schedules"),
        "fixtures": relationship("Fixture", back_populates="schedule", uselist=True),
        "team_standings": relationship("Standings", back_populates="schedule"),
    },
)
