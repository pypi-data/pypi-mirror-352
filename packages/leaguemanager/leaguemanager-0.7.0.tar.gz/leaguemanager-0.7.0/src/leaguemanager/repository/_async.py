from advanced_alchemy.repository import (
    SQLAlchemyAsyncRepository,
    SQLAlchemyAsyncSlugRepository,
)

from leaguemanager import models

__all__ = [
    "AddressAsyncRepository",
    "CityAsyncRepository",
    "CountryAsyncRepository",
    "FixtureTeamAsyncRepository",
    "FixtureAsyncRepository",
    "LeagueAsyncRepository",
    "ManagerAsyncRepository",
    "OrganizationAsyncRepository",
    "PlayerAsyncRepository",
    "RefereeAsyncRepository",
    "RoleAsyncRepository",
    "RulesetAsyncRepository",
    "ScheduleAsyncRepository",
    "SeasonAsyncRepository",
    "StandingsAsyncRepository",
    "StateAsyncRepository",
    "TeamAsyncRepository",
    "UserAsyncRepository",
    "UserRoleAsyncRepository",
]


class AddressAsyncRepository(SQLAlchemyAsyncRepository[models.Address]):
    """Address repository."""

    model_type = models.Address


class CityAsyncRepository(SQLAlchemyAsyncRepository[models.City]):
    """City repository."""

    model_type = models.City


class CountryAsyncRepository(SQLAlchemyAsyncRepository[models.Country]):
    """Country repository."""

    model_type = models.Country


class FixtureTeamAsyncRepository(SQLAlchemyAsyncRepository[models.FixtureTeam]):
    """FixtureTeam repository."""

    model_type = models.FixtureTeam


class FixtureAsyncRepository(SQLAlchemyAsyncRepository[models.Fixture]):
    """Fixture repository."""

    model_type = models.Fixture


class LeagueAsyncRepository(SQLAlchemyAsyncSlugRepository[models.League]):
    """League repository."""

    model_type = models.League


class ManagerAsyncRepository(SQLAlchemyAsyncRepository[models.Manager]):
    """Manager repository."""

    model_type = models.Manager


class OrganizationAsyncRepository(SQLAlchemyAsyncSlugRepository[models.Organization]):
    """Organization repository."""

    model_type = models.Organization


class PlayerAsyncRepository(SQLAlchemyAsyncRepository[models.Player]):
    """Player repository."""

    model_type = models.Player


class RefereeAsyncRepository(SQLAlchemyAsyncRepository[models.Referee]):
    """Referee repository."""

    model_type = models.Referee


class RoleAsyncRepository(SQLAlchemyAsyncSlugRepository[models.Role]):
    """Role repository."""

    model_type = models.Role


class RulesetAsyncRepository(SQLAlchemyAsyncRepository[models.Ruleset]):
    """Ruleset repository."""

    model_type = models.Ruleset


class ScheduleAsyncRepository(SQLAlchemyAsyncRepository[models.Schedule]):
    """Schedule repository."""

    model_type = models.Schedule


class SeasonAsyncRepository(SQLAlchemyAsyncSlugRepository[models.Season]):
    """Season repository."""

    model_type = models.Season


class StandingsAsyncRepository(SQLAlchemyAsyncRepository[models.Standings]):
    """Standings repository."""

    model_type = models.Standings


class StateAsyncRepository(SQLAlchemyAsyncRepository[models.State]):
    """State repository."""

    model_type = models.State


class TeamAsyncRepository(SQLAlchemyAsyncSlugRepository[models.Team]):
    """Team repository."""

    model_type = models.Team


class UserRoleAsyncRepository(SQLAlchemyAsyncRepository[models.UserRole]):
    """UserRole repository."""

    model_type = models.UserRole


class UserAsyncRepository(SQLAlchemyAsyncRepository[models.User]):
    """User repository."""

    model_type = models.User
