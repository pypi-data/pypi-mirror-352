from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from attrs import define, field, validators
from sqlalchemy import UUID as _UUID
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship
from typing_extensions import TYPE_CHECKING

from leaguemanager.models.base import UUIDAuditBase, mapper, metadata
from leaguemanager.models.enums import Field, FixtureStatus

from ._association import fixture_referee

if TYPE_CHECKING:
    from .fixture_team import FixtureTeam
    from .league import League
    from .player import Player
    from .referee import Referee
    from .schedule import Schedule
    from .season import Season
    from .team import Team


@define(slots=False)
class Fixture(UUIDAuditBase):
    """Represents a specific match in a schedule."""

    season_id: UUID | None = field(default=None)
    league_id: UUID | None = field(default=None)
    schedule_id: UUID | None = field(default=None)

    home_team_id: UUID | None = field(default=None)
    away_team_id: UUID | None = field(default=None)

    bye_week: bool = field(default=False)

    home_goals: int | None = field(default=None)
    away_goals: int | None = field(default=None)

    matchday: int | None = field(default=None)
    date: str | None = field(default=None)
    status: FixtureStatus = field(
        default=FixtureStatus.U.name, validator=validators.in_([v.name for v in FixtureStatus])
    )
    field: Field = field(default=Field.A.name, validator=validators.in_([v.name for v in Field]))


# SQLAlchemy Imperative Mappings

fixture = Table(
    "fixture",
    metadata,
    Column("id", _UUID, primary_key=True),
    Column("season_id", _UUID, ForeignKey("season.id")),
    Column("league_id", _UUID, ForeignKey("league.id")),
    Column("schedule_id", _UUID, ForeignKey("schedule.id", ondelete="cascade")),
    Column("home_team_id", _UUID, ForeignKey("team.id", ondelete="set null")),
    Column("away_team_id", _UUID, ForeignKey("team.id", ondelete="set null")),
    Column("bye_week", Boolean),
    Column("home_goals", Integer),
    Column("away_goals", Integer),
    Column("matchday", Integer),
    Column("date", DateTime),
    Column("field", String(2)),
    Column("status", String(10)),
    Column("created_at", DateTime, default=lambda: datetime.now(UTC)),
    Column("updated_at", DateTime, default=lambda: datetime.now(UTC), onupdate=datetime.now(UTC)),
)


# ORM Relationships

mapper.map_imperatively(
    Fixture,
    fixture,
    properties={
        "schedule": relationship("Schedule", back_populates="fixtures"),
        "referees": relationship("Referee", secondary=fixture_referee, back_populates="fixtures"),
        "teams": relationship("FixtureTeam", back_populates="fixture", cascade="all, delete"),
    },
)
