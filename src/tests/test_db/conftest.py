import uuid
from typing import TYPE_CHECKING, Any, Protocol

import pytest
from mimesis import Datetime, Locale, Text

from app.core.models.tables.tests import TestBaseModel, TestRelatedModel
from tests.utils.database import db_create_item

if TYPE_CHECKING:
    from collections.abc import Awaitable

    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

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


text_provider = Text(locale=Locale.RU)
datetime_provider = Datetime(locale=Locale.RU)


@pytest.fixture()
def test_base_model_factory(
    db_session_factory: 'async_sessionmaker[AsyncSession]',
) -> 'TestBaseModelFactoryProtocol':
    """Фабрика создания тестового экземпляра модели."""

    async def create_item(**kwargs: Any) -> 'TestBaseModel':  # noqa: ANN401
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
