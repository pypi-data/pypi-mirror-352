import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from leaguemanager.db import register_sqlite
from leaguemanager.models.base import metadata
from leaguemanager.services import (
    FixtureSyncService,
    FixtureTeamSyncService,
    LeagueSyncService,
    ScheduleSyncService,
    SeasonSyncService,
    StandingsSyncService,
    TeamSyncService,
)

pytest_plugins = ["tests.data_fixtures"]

register_sqlite()


@pytest.fixture(scope="session")
def db_dir(tmp_path_factory):
    db_dir = tmp_path_factory.mktemp("db_test")
    return db_dir


# Sync DB fixtures


@pytest.fixture(scope="session")
def engine(db_dir):
    uri = f"sqlite:///{db_dir / 'test.db'}"
    engine = create_engine(uri, echo=False)
    metadata.drop_all(engine)
    metadata.create_all(engine)
    yield engine
    metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture(scope="session")
def session_factory(engine):
    return sessionmaker(bind=engine, expire_on_commit=True, autocommit=False, autoflush=False)


@pytest.fixture(scope="session", autouse=True)
def session(session_factory, all_data):
    session_ = session_factory()
    yield session_
    session_.rollback()
    session_.close()


@pytest.fixture(scope="session")
def season_service(session):
    return SeasonSyncService(session=session)


@pytest.fixture(scope="session")
def team_service(session):
    return TeamSyncService(session=session)


@pytest.fixture(scope="session")
def league_service(session):
    return LeagueSyncService(session=session)


@pytest.fixture(scope="session")
def schedule_service(session):
    return ScheduleSyncService(session=session)


@pytest.fixture(scope="session")
def fixture_service(session):
    return FixtureSyncService(session=session)


@pytest.fixture(scope="session")
def fixture_team_service(session):
    return FixtureTeamSyncService(session=session)


@pytest.fixture(scope="session")
def standings_service(session):
    return StandingsSyncService(session=session)
