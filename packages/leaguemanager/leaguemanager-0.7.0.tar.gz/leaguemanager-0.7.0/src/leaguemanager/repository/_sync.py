from advanced_alchemy.repository import (
    SQLAlchemySyncRepository,
    SQLAlchemySyncSlugRepository,
)

from leaguemanager import models

__all__ = [
    "AddressSyncRepository",
    "CitySyncRepository",
    "CountrySyncRepository",
    "FixtureTeamSyncRepository",
    "FixtureSyncRepository",
    "LeagueSyncRepository",
    "ManagerSyncRepository",
    "OrganizationSyncRepository",
    "PlayerSyncRepository",
    "RefereeSyncRepository",
    "RoleSyncRepository",
    "RulesetSyncRepository",
    "ScheduleSyncRepository",
    "SeasonSyncRepository",
    "StateSyncRepository",
    "TeamSyncRepository",
    "StandingsSyncRepository",
    "UserRoleSyncRepository",
    "UserSyncRepository",
]


class AddressSyncRepository(SQLAlchemySyncRepository[models.Address]):
    """Address repository."""

    model_type = models.Address


class CitySyncRepository(SQLAlchemySyncRepository[models.City]):
    """City repository."""

    model_type = models.City


class CountrySyncRepository(SQLAlchemySyncRepository[models.Country]):
    """Country repository."""

    model_type = models.Country


class FixtureTeamSyncRepository(SQLAlchemySyncRepository[models.FixtureTeam]):
    """FixtureTeam repository."""

    model_type = models.FixtureTeam


class FixtureSyncRepository(SQLAlchemySyncRepository[models.Fixture]):
    """Fixture repository."""

    model_type = models.Fixture


class LeagueSyncRepository(SQLAlchemySyncSlugRepository[models.League]):
    """League repository."""

    model_type = models.League


class ManagerSyncRepository(SQLAlchemySyncRepository[models.Manager]):
    """Manager repository."""

    model_type = models.Manager


class OrganizationSyncRepository(SQLAlchemySyncSlugRepository[models.Organization]):
    """Organization repository."""

    model_type = models.Organization


class PlayerSyncRepository(SQLAlchemySyncRepository[models.Player]):
    """Player repository."""

    model_type = models.Player


class RefereeSyncRepository(SQLAlchemySyncRepository[models.Referee]):
    """Referee repository."""

    model_type = models.Referee


class RoleSyncRepository(SQLAlchemySyncSlugRepository[models.Role]):
    """Role repository."""

    model_type = models.Role


class RulesetSyncRepository(SQLAlchemySyncRepository[models.Ruleset]):
    """Ruleset repository."""

    model_type = models.Ruleset


class ScheduleSyncRepository(SQLAlchemySyncRepository[models.Schedule]):
    """Schedule repository."""

    model_type = models.Schedule


class SeasonSyncRepository(SQLAlchemySyncSlugRepository[models.Season]):
    """Season repository."""

    model_type = models.Season


class StandingsSyncRepository(SQLAlchemySyncRepository[models.Standings]):
    """Standings repository."""

    model_type = models.Standings


class StateSyncRepository(SQLAlchemySyncRepository[models.State]):
    """State repository."""

    model_type = models.State


class TeamSyncRepository(SQLAlchemySyncSlugRepository[models.Team]):
    """Team repository."""

    model_type = models.Team


class UserRoleSyncRepository(SQLAlchemySyncRepository[models.UserRole]):
    """UserRole repository."""

    model_type = models.UserRole


class UserSyncRepository(SQLAlchemySyncRepository[models.User]):
    """User repository."""

    model_type = models.User
