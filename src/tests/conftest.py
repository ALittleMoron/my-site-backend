import asyncio
import contextlib
from asyncio import AbstractEventLoop, current_task
from typing import TYPE_CHECKING, TypeVar

import asyncpg
import pytest
import pytest_asyncio
from app.api.v1.dependencies.databases import get_session as app_get_session
from app.core.config import get_database_settings, get_logger
from app.core.models import tables
from app.main import get_application
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_scoped_session,
    async_sessionmaker,
    create_async_engine,
)

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator, Generator

    from sqlalchemy.ext.asyncio import AsyncEngine

    BaseSQLAlchemyModel = TypeVar('BaseSQLAlchemyModel', bound=tables.Base)


logger = get_logger('tests')


@pytest.fixture(scope='session')
def test_models() -> list[tables.Base]:
    """Тестовые модели для использовании при создании схем в тестовой базе данных."""
    from app.core.models.tables.tests import TestBaseModel, TestRelatedModel

    return [TestBaseModel, TestRelatedModel]  # type: ignore


@pytest.fixture(scope="session")
def event_loop() -> 'Generator[AbstractEventLoop, None, None]':
    """Переписанная фикстура event_loop для работы остальных фикстур."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope='session')
def db_url() -> str:
    """Фикстура, возвращающая url к тестовой базе данных."""
    database_settings = get_database_settings()
    return database_settings.test_db_url


@pytest.fixture(scope='session')
def db_name() -> str:
    """Фикстура, возвращающая название тестовой базы данных."""
    return 'pytest_db'


@pytest_asyncio.fixture(scope='session')  # type: ignore
async def db_engine(
    db_url: str,
    db_name: str,
) -> 'AsyncGenerator[AsyncEngine, None]':
    """Инициализация коннектора тестовой БД."""
    database_settings = get_database_settings()
    with contextlib.suppress(Exception):
        pool = await asyncpg.create_pool(database_settings.asyncpg_postgresql_url)
        if pool:
            async with pool.acquire() as conn:
                await conn.execute(f'CREATE DATABASE {db_name}')
            await pool.close()
    engine = create_async_engine(db_url, echo=False, pool_pre_ping=True)
    try:
        yield engine
    finally:
        await engine.dispose()
    with contextlib.suppress(Exception):
        pool = await asyncpg.create_pool(database_settings.asyncpg_postgresql_url)
        if pool:
            async with pool.acquire() as conn:
                await conn.execute(f'DROP DATABASE IF EXISTS {db_name}')
            await pool.close()  # type: ignore


@pytest.fixture(scope='session')
def db_session_factory(db_engine: 'AsyncEngine') -> 'async_scoped_session[AsyncSession]':
    """Фабрика тестовых сессий."""
    return async_scoped_session(
        async_sessionmaker(
            bind=db_engine,
            autocommit=False,
            autoflush=False,
            expire_on_commit=False,
        ),
        current_task,
    )


@pytest_asyncio.fixture()  # type: ignore
async def db_session(
    db_session_factory: 'async_scoped_session[AsyncSession]',
) -> 'AsyncGenerator[AsyncSession, None]':
    """Сессия тестовой БД."""
    async with db_session_factory() as session:
        yield session


@pytest_asyncio.fixture()  # type: ignore
async def testing_app(
    test_models: list[tables.Base],
    db_engine: 'AsyncEngine',
    db_session_factory: 'async_scoped_session[AsyncSession]',
) -> 'AsyncGenerator[TestClient, None]':
    """Фикстура-менеджер создания тестового клиента."""
    async with db_engine.begin() as conn:
        await conn.run_sync(tables.Base.metadata.create_all)
    app = get_application()

    async def get_session() -> 'AsyncGenerator[AsyncSession, None]':
        """Получение сессии соединения с тестовой БД."""
        async with db_session_factory() as session:
            yield session

    app.dependency_overrides[app_get_session] = get_session
    client = TestClient(app)
    yield client
    async with db_engine.begin() as conn:
        await conn.run_sync(tables.Base.metadata.drop_all)
