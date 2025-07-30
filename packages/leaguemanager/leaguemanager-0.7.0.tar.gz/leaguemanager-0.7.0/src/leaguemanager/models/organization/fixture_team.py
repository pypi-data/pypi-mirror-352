from __future__ import annotations

from uuid import UUID

from attrs import define, field, validators
from sqlalchemy import UUID as _UUID
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Table
from sqlalchemy.orm import relationship
from typing_extensions import TYPE_CHECKING

from leaguemanager.models.base import UUIDBase, mapper, metadata
from leaguemanager.models.enums import FixtureResult

if TYPE_CHECKING:
    from .fixture import Fixture
    from .team import Team


@define(slots=False)
class FixtureTeam(UUIDBase):
    """Results for a fixture for specific team (association table)."""

    team_id: UUID | None = field(default=None)
    fixture_id: UUID | None = field(default=None)

    is_played: bool = field(default=False)
    fixture_result: FixtureResult | None = field(
        default=None, validator=validators.optional(validators.in_([v.name for v in FixtureResult]))
    )
    points: int | None = field(default=0)
    score_for: int | None = field(default=0)
    score_against: int | None = field(default=0)


# SQLAlchemy Imperative Mappings

fixture_team = Table(
    "fixture_team",
    metadata,
    Column("id", _UUID, primary_key=True),
    Column("team_id", _UUID, ForeignKey("team.id")),
    Column("fixture_id", _UUID, ForeignKey("fixture.id")),
    Column("is_played", Boolean),
    Column("fixture_result", String(10)),
    Column("points", Integer),
    Column("score_for", Integer),
    Column("score_against", Integer),
)

# ORM Relationships

mapper.map_imperatively(
    FixtureTeam,
    fixture_team,
    properties={
        "team": relationship("Team", back_populates="fixtures"),
        "fixture": relationship("Fixture", back_populates="teams"),
    },
)
