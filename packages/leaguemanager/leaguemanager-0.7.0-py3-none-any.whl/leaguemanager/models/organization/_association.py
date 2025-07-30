from sqlalchemy import Column, ForeignKey, MetaData, Table
from sqlalchemy.types import UUID as _UUID

from ..base import metadata

# Association tables

player_team = Table(
    "player_team",
    metadata,
    Column("player_id", _UUID, ForeignKey("player.id"), primary_key=True),
    Column("team_id", _UUID, ForeignKey("team.id"), primary_key=True),
)

fixture_referee = Table(
    "fixture_referees",
    metadata,
    Column("fixture_id", _UUID, ForeignKey("fixture.id"), primary_key=True),
    Column("referee_id", _UUID, ForeignKey("referee.id"), primary_key=True),
)
