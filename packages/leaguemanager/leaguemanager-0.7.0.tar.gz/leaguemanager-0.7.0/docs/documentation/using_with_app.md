# Incorporating With Your App

You can also install League Manager as a [dependency](#installing-from-pip) for your project. This allows you to incorporate the League Manager backend into your own application.

:::{warning}
Currently, the League Manager backend is _skewed_ toward running a soccer league ⚽. What this means is certain tables include optional fields defining league rules.

However, since the fields are optional, League Manager can still be used to organize a wide variety of leagues, and more customizations will be added in the future
:::

## Accessing Services

Under the hood, League Manager utilizes the [svcs library](https://svcs.hynek.me/en/stable/) to serve up a database session, as well as preconfigured database services offering easy-to-use, preconfigured CRUD operations on each of the provided models.

The really cool part here :sparkles: is the inclusion of autocomplete. Once you have retrieved your required service, your IDE will assist you with all the prebuilt database operations.

(You can also look at [Advanced Alchemy's documentation](https://docs.advanced-alchemy.litestar.dev/latest/reference/service.html#advanced_alchemy.service.SQLAlchemySyncRepositoryService) for an idea of what's included.)

Here is an example of how to access those services directly:

```python
from leaguemanager import LeagueManager
from leaguemanager.services import SeasonSyncService, TeamSyncService

registry = LeagueManager()
season_service = registry.provide_db_service(SeasonSyncService)
team_service = registry.provide_db_service(TeamSyncService)

# This will return the number of seasons saved in the database
number_of_seasons = season_service.count()

# This will return a list of `Season` objects (models)
seasons = season_service.list()

# Total number of teams in the database
number_of_teams = team_service.count()

# You get the idea
teams = team_service.list()

# Print all the team names
for team in teams:
    print(team.name)
```

The `provide_db_service` is able to look at the `type` of service passed in (in this case, both `SeasonSyncService` and `TeamSyncService`), and now you have access to many typical CRUD operations and filters for that specific table.

Some of the services also include additional business logic specific to League Manager applications.

If you only need the database session (a SQLAlchemy `Session` type) to do your own custom logic using SQLAlchemy, you can also use the registry.

```python
# Using the db session directly

session = registry.provide_db_session
session.execute(delete(SomeModel))
```
