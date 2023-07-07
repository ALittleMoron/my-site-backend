import contextlib
import os
import random
from asyncio import current_task
from typing import TYPE_CHECKING, Any, TypeVar

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_scoped_session,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy_utils.functions import create_database, drop_database  # type: ignore

from app.api.v1.dependencies.databases import get_session as app_get_session
from app.core.models import tables
from app.main import get_application

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator, Generator

    from sqlalchemy.ext.asyncio import AsyncEngine

    BaseSQLAlchemyModel = TypeVar('BaseSQLAlchemyModel', bound=tables.Base)

TEST_DATABASE_URL = 'postgresql+asyncpg://postgres:somedbpass@localhost:5432/test_db'


def coin_flip() -> bool:
    """Возвращает случайное булево значение."""
    return bool(random.getrandbits(1))


async def db_create_item(
    db_session_factory: 'async_sessionmaker[AsyncSession]',
    model: 'type[BaseSQLAlchemyModel]',
    params: dict[str, Any],
) -> 'BaseSQLAlchemyModel':
    """Создает запись в базе данных из модели и параметров."""
    async with db_session_factory() as db_:
        item = model(**params)
        db_.add(item)
        try:
            await db_.commit()
            await db_.flush()
            await db_.refresh(item)
        except SQLAlchemyError:
            await db_.rollback()
            raise
        else:
            return item


@pytest.fixture(scope='session')
def db_url() -> str:
    """Фикстура, возвращающая url к тестовой базе данных."""
    return os.getenv('PYTEST_DBURL', default=TEST_DATABASE_URL)


@pytest.fixture(scope='session')
def _create_test_db(db_url: str) -> 'Generator[None, None, None]':  # type: ignore
    """Фикстура-менеджер тестовой базы данных."""
    with contextlib.suppress(Exception):
        drop_database(db_url)  # type: ignore

    create_database(db_url)  # type: ignore
    yield
    drop_database(db_url)  # type: ignore


@pytest.fixture(scope='session')
async def db_engine(db_url: str) -> 'AsyncGenerator[AsyncEngine, None]':
    """Инициализация коннектора тестовой БД."""
    engine_ = create_async_engine(db_url, echo=True, pool_pre_ping=True)

    yield engine_

    await engine_.dispose()


@pytest.fixture(scope='session')
async def db_session_factory(db_engine: 'AsyncEngine') -> 'async_scoped_session[AsyncSession]':
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


@pytest.fixture()
async def db_session(
    db_session_factory: 'async_scoped_session[AsyncSession]',
) -> 'AsyncGenerator[AsyncSession, None]':
    """Сессия тестовой БД."""
    async with db_session_factory() as session:
        yield session


@pytest.fixture()
async def testing_app(
    _create_test_db: 'Generator[None, None, None]',
    db_session_factory: 'async_scoped_session[AsyncSession]',
) -> 'AsyncGenerator[TestClient, None]':
    """Фикстура-менеджер создания тестового клиента."""
    engine = create_async_engine(TEST_DATABASE_URL)
    async with engine.begin() as conn:
        await conn.run_sync(tables.Base.metadata.create_all)  # type: ignore

        app = get_application()

        async def get_session() -> 'AsyncGenerator[AsyncSession, None]':
            """Получение сессии соединения с тестовой БД."""
            async with db_session_factory() as session:
                yield session

        app.dependency_overrides[app_get_session] = get_session
        client = TestClient(app)
        yield client
        await conn.run_sync(tables.Base.metadata.drop_all)  # type: ignore
