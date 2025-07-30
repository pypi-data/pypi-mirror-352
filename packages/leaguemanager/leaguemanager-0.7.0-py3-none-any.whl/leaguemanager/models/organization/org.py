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
    from ..account.address import Address
    from .league import League
    from .season import Season


@define(slots=False)
class Organization(UUIDAuditBase):
    """Defines an organization with certain rules, as well as divisions and categories."""

    name: str | None = field(default=None, validator=validators.max_len(80))
    description: str | None = field(default=None, validator=validators.optional(validators.max_len(255)))


organization = Table(
    "organization",
    metadata,
    Column("id", SA_UUID, primary_key=True),
    Column("name", String(80), nullable=False, unique=True),
    Column("description", String(255), nullable=True),
    Column("created_at", DateTime, default=lambda: datetime.now(UTC)),
    Column("updated_at", DateTime, default=lambda: datetime.now(UTC), onupdate=datetime.now(UTC)),
)

# ORM Relationships
mapper.map_imperatively(
    Organization,
    organization,
    properties={
        "seasons": relationship("Season", back_populates="organization"),
        "address": relationship("Address", back_populates="organization"),
    },
)
