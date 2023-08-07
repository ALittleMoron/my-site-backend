import asyncio
import contextlib
import uuid
from asyncio import AbstractEventLoop, current_task
from typing import TYPE_CHECKING, Any, Protocol, TypeVar

import asyncpg
import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from mimesis import Locale, Text
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_scoped_session,
    async_sessionmaker,
    create_async_engine,
)

from app.api.v1.dependencies.databases import get_session as app_get_session
from app.core.config import get_database_settings, get_logger
from app.core.models import tables
from app.core.models.tables.tests import TestBaseModel, TestRelatedModel
from app.main import get_application
from tests.utils.database import db_create_item

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator, Awaitable, Generator

    from sqlalchemy.ext.asyncio import AsyncEngine

    BaseSQLAlchemyModel = TypeVar('BaseSQLAlchemyModel', bound=tables.Base)

    class TestBaseModelFactoryProtocol(Protocol):  # noqa
        def __call__(self, **kwargs: Any) -> 'Awaitable[TestBaseModel]':  # noqa
            ...

    class TestBaseModelListFactoryProtocol(Protocol):  # noqa
        def __call__(  # noqa
            self,  # noqa
            count: int = 1,
            **kwargs: Any,  # noqa
        ) -> 'Awaitable[list[TestBaseModel]]':
            ...

    class TestRelatedModelFactoryProtocol(Protocol):  # noqa
        def __call__(  # noqa
            self,  # noqa
            test_base_model_id: uuid.UUID | None = None,
            **kwargs: Any,  # noqa
        ) -> 'Awaitable[TestRelatedModel]':
            ...

    class TestRelatedModelListFactoryProtocol(Protocol):  # noqa
        def __call__(  # noqa
            self,  # noqa
            count: int = 1,
            test_base_model_id: uuid.UUID | None = None,
            **kwargs: Any,  # noqa
        ) -> 'Awaitable[list[TestRelatedModel]]':
            ...


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


@pytest.fixture()
def test_base_model_factory(
    db_session_factory: 'async_sessionmaker[AsyncSession]',
) -> 'TestBaseModelFactoryProtocol':
    """Фабрика создания тестового экземпляра модели."""

    async def create_item(**kwargs: Any) -> 'TestBaseModel':  # noqa: ANN401
        text_provider = Text(locale=Locale.RU)
        params = dict(text=text_provider.text(quantity=3))
        params.update(kwargs)
        item = await db_create_item(db_session_factory, TestBaseModel, params)
        return item

    return create_item


@pytest.fixture()
def test_base_model_list_factory(
    test_base_model_factory: 'TestBaseModelFactoryProtocol',
) -> 'TestBaseModelListFactoryProtocol':
    """Фабрика создания тестового списка экземпляров модели."""

    async def create_item(count: int = 1, **kwargs: Any) -> 'list[TestBaseModel]':  # noqa: ANN401
        return [await test_base_model_factory(**kwargs) for _ in range(count)]

    return create_item


@pytest.fixture()
def test_related_model_factory(
    db_session_factory: 'async_sessionmaker[AsyncSession]',
    test_base_model_factory: 'TestBaseModelFactoryProtocol',
) -> 'TestRelatedModelFactoryProtocol':
    """Фабрика создания тестового экземпляра модели со связью."""

    async def create_item(
        test_base_model_id: uuid.UUID | None = None,
        **kwargs: Any,  # noqa: ANN401
    ) -> 'TestRelatedModel':
        text_provider = Text(locale=Locale.RU)
        if not test_base_model_id:
            test_base_model = await test_base_model_factory()
            test_base_model_id = test_base_model.id
        params = dict(
            test_base_model_id=test_base_model_id,
            text=text_provider.text(quantity=3),
        )
        params.update(kwargs)
        item = await db_create_item(db_session_factory, TestRelatedModel, params)
        return item

    return create_item


@pytest.fixture()
def test_related_model_list_factory(
    test_base_model_factory: 'TestRelatedModelFactoryProtocol',
) -> 'TestRelatedModelListFactoryProtocol':
    """Фабрика создания тестового списка экземпляров модели."""

    async def create_item(
        count: int = 1,
        test_base_model_id: uuid.UUID | None = None,
        **kwargs: Any,  # noqa: ANN401
    ) -> 'list[TestRelatedModel]':
        return [
            await test_base_model_factory(test_base_model_id=test_base_model_id, **kwargs)
            for _ in range(count)
        ]

    return create_item
