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
    from ..enums import Category, Division
    from .league import League


@define(slots=False)
class Ruleset(UUIDAuditBase):
    """Defines a set of rules/parameters for leagues."""

    league_id: UUID | None = field(default=None)
    name: str | None = field(default=None, validator=validators.max_len(80))
    description: str | None = field(default=None, validator=validators.max_len(255))

    team_size: int = field(default=5)

    category: Category = field(
        default=Category.COED,
        validator=validators.instance_of(Category),
    )

    division: Division = field(
        default=Division.A,
        validator=validators.instance_of(Division),
    )

    match_day: list[MatchDay] = field(
        default=[MatchDay.SUN],
        validator=validators.deep_iterable(
            member_validator=validators.instance_of(MatchDay),
            iterable_validator=validators.instance_of(list),
        ),
    )

    schedule_type: str = field(default="ROUND_ROBIN", validator=validators.max_len(20))

    division_name: str | None = field(
        default=None,
        validator=validators.optional(validators.max_len(80)),
    )

    coed_male_count_min: int | None = field(default=None)
    coed_female_count_min: int | None = field(default=None)

    m_age_rule_min: int | None = field(default=None)
    m_age_rule_max: int | None = field(default=None)
    f_age_rule_min: int | None = field(default=None)
    f_age_rule_max: int | None = field(default=None)


# SQLAlchemy Imperative Mapping

ruleset = Table(
    "ruleset",
    metadata,
    Column("id", SA_UUID, primary_key=True),
    Column("league_id", SA_UUID, ForeignKey("league.id"), nullable=True),
    Column("name", String(80), nullable=False, unique=True),
    Column("description", String(255), nullable=True),
    Column("team_size", Integer, default=5, nullable=False),
    Column("category", String(20), nullable=False),
    Column("division", String(20), nullable=False),
    Column("match_day", String(100), nullable=False, default="SUN"),
    Column("schedule_type", String(20), nullable=False, default="ROUND_ROBIN"),
    Column("division_name", String(80), nullable=True),
    Column("coed_male_count_min", Integer, nullable=True),
    Column("coed_female_count_min", Integer, nullable=True),
    Column("m_age_rule_min", Integer, nullable=True),
    Column("m_age_rule_max", Integer, nullable=True),
    Column("f_age_rule_min", Integer, nullable=True),
    Column("f_age_rule_max", Integer, nullable=True),
    Column("created_at", DateTime, default=lambda: datetime.now(UTC)),
    Column("updated_at", DateTime, default=lambda: datetime.now(UTC), onupdate=datetime.now(UTC)),
)

mapper.map_imperatively(
    Ruleset,
    ruleset,
    properties={
        "leagues": relationship("League", back_populates="ruleset"),
    },
)
