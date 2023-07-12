from typing import TYPE_CHECKING, Any, Protocol

import pytest
from app.core.exceptions.repositories import RepositorySubclassNotSetAttributeError
from app.core.models.tables.tests import Base, TestBaseModel, TestRelatedModel
from app.db.repositories.base import BaseRepository, SelectModeEnum
from mimesis import Datetime, Locale
from sqlalchemy.orm import joinedload

if TYPE_CHECKING:
    import uuid
    from collections.abc import Awaitable, Sequence

    from fastapi.testclient import TestClient
    from sqlalchemy.ext.asyncio import AsyncSession
    from sqlalchemy.orm.attributes import InstrumentedAttribute
    from sqlalchemy.orm.strategy_options import _AbstractLoad  # type: ignore
    from sqlalchemy.sql.elements import ColumnElement
    from sqlalchemy.sql.functions import Function

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

    JoinKwargs = dict[str, Any]
    Model = type[Base]
    JoinClause = ColumnElement[bool]
    ModelWithOnclause = tuple[Model, JoinClause]
    CompleteModel = tuple[Model, JoinClause, JoinKwargs]
    Join = Model | ModelWithOnclause | CompleteModel


fake_datetimes = Datetime(Locale.EN)


class TestRepository(BaseRepository[TestBaseModel]):
    """Тестовый репозиторий."""

    __test__ = False
    model_class = TestBaseModel

    async def get_item(  # noqa
        self: 'TestRepository',
        *,
        item_id: 'uuid.UUID',
        joins: 'Sequence[Join] | None' = None,
        options: 'Sequence[_AbstractLoad] | None' = None,
        select_mode: SelectModeEnum = SelectModeEnum.BRIEF,
    ) -> TestBaseModel | None:
        result = await self._get_item(
            item_identity=item_id,
            joins=joins,
            options=options,
            select_mode=select_mode,
        )
        return result

    async def get_db_items_count(  # noqa
        self: 'TestRepository',
        *,
        joins: 'Sequence[Join] | None' = None,
        filters: 'Sequence[ColumnElement[bool]] | None' = None,
    ) -> int:
        result = await self._get_db_items_count(
            joins=joins,
            filters=filters,
        )
        return result

    async def get_item_list(  # noqa
        self: 'TestRepository',
        *,
        joins: 'Sequence[Join] | None' = None,
        options: 'Sequence[_AbstractLoad] | None' = None,
        filters: 'Sequence[ColumnElement[bool]] | None' = None,
        search: str | None = None,
        search_by: 'Sequence[str | InstrumentedAttribute[Any] | Function[Any]] | None' = None,
        order_by: 'Sequence[str | ColumnElement[Any] | InstrumentedAttribute[Any]] | None' = None,
        limit: int | None = None,
        offset: int | None = None,
        select_mode: SelectModeEnum = SelectModeEnum.BRIEF,
    ) -> 'Sequence[TestBaseModel]':
        result = await self._get_item_list(
            joins=joins,
            options=options,
            filters=filters,
            search=search,
            search_by=search_by,
            order_by=order_by,
            limit=limit,
            offset=offset,
            select_mode=select_mode,
        )
        return result


def test_base_query_item_identity_error(
    testing_app: 'TestClient',
    db_session: 'AsyncSession',
) -> None:
    """Проверка передачи невалидного item_identity_field.."""
    repo = TestRepository(db_session)
    with pytest.raises(ValueError, match='abc не является полем модели TestBaseModel'):
        repo.base_queries._get_item_identity_filter(  # type: ignore
            model=TestBaseModel,
            item_identity=25,
            item_identity_field="abc",
        )


def test_repository_model_class_attribute_error() -> None:
    """Проверка выбрасывания ошибки при попытке создать репозиторий без model_class."""
    with pytest.raises(RepositorySubclassNotSetAttributeError):

        class TestFailRepository(BaseRepository[TestBaseModel]):  # type: ignore
            """Тестовый репозиторий."""

            __test__ = False


@pytest.mark.asyncio()
async def test_get_one_item(
    testing_app: 'TestClient',
    db_session: 'AsyncSession',
    test_base_model_factory: 'TestBaseModelFactoryProtocol',
) -> None:
    """Проверка получения одного элемента."""
    repo = TestRepository(db_session)
    item = await test_base_model_factory()
    received_item = await repo.get_item(item_id=item.id)  # type: ignore
    if received_item is None:
        pytest.fail('метод _get_item должен точно вернуть элемент в данном кейсе.')
    assert item.id == received_item.id


@pytest.mark.asyncio()
async def test_one_joined_item(
    testing_app: 'TestClient',
    db_session: 'AsyncSession',
    test_base_model_factory: 'TestBaseModelFactoryProtocol',
    test_related_model_factory: 'TestRelatedModelFactoryProtocol',
) -> None:
    """Проверка получения одного элемента с отношением."""
    repo = TestRepository(db_session)
    item = await test_base_model_factory()
    related = await test_related_model_factory(test_base_model_id=item.id)
    received_item = await repo.get_item(  # type: ignore
        item_id=item.id,
        joins=((TestRelatedModel, TestRelatedModel.test_base_model_id == TestBaseModel.id),),
        options=(joinedload(TestBaseModel.test_related_models),),
        select_mode=SelectModeEnum.VERBOSE,
    )
    if received_item is None:
        pytest.fail('метод _get_item должен точно вернуть элемент в данном кейсе.')
    if not received_item.test_related_models:
        pytest.fail('метод _get_item должен точно объединить таблицы между собой.')
    assert item.id == received_item.id
    assert len(received_item.test_related_models) == 1
    received_related = received_item.test_related_models[0]
    assert related.id == received_related.id
    assert related.test_base_model_id == received_related.test_base_model_id


@pytest.mark.asyncio()
async def test_get_item_list(
    testing_app: 'TestClient',
    db_session: 'AsyncSession',
    test_base_model_list_factory: 'TestBaseModelListFactoryProtocol',
) -> None:
    """Проверка получения списка элементов."""
    repo = TestRepository(db_session)
    items = await test_base_model_list_factory(count=2)
    item_ids = {item.id for item in items}
    assert len(item_ids) == 2
    received_items = await repo.get_item_list()  # type: ignore
    for received_item in received_items:
        assert received_item.id in item_ids


@pytest.mark.asyncio()
async def test_get_items_count(
    testing_app: 'TestClient',
    db_session: 'AsyncSession',
    test_base_model_list_factory: 'TestBaseModelListFactoryProtocol',
) -> None:
    """Проверка получения количества записей в базе."""
    repo = TestRepository(db_session)
    items = await test_base_model_list_factory(count=2)
    item_ids = {item.id for item in items}
    assert len(item_ids) == 2
    count = await repo.get_db_items_count()  # type: ignore
    assert count == len(item_ids)


@pytest.mark.asyncio()
async def test_get_items_count_filtered(
    testing_app: 'TestClient',
    db_session: 'AsyncSession',
    test_base_model_list_factory: 'TestBaseModelListFactoryProtocol',
) -> None:
    """Проверка получения количества записей в базе с фильтрацией."""
    repo = TestRepository(db_session)
    items = await test_base_model_list_factory(count=2, disabled_at=None)
    for item in items:
        assert item.disabled_at is None
    disabled_items = await test_base_model_list_factory(
        count=2,
        disabled_at=fake_datetimes.datetime(),
    )
    for disabled_item in disabled_items:
        assert disabled_item.disabled_at is not None
    item_ids = {item.id for item in items}
    assert len(item_ids) == 2
    assert len(disabled_items) == 2
    count = await repo.get_db_items_count(
        filters=(TestBaseModel.disabled_at.is_not(None),),
    )
    disabled_count = await repo.get_db_items_count(
        filters=(TestBaseModel.disabled_at.is_(None),),
    )
    assert count == len(item_ids)
    assert disabled_count == len(disabled_items)


@pytest.mark.asyncio()
async def test_get_items_count_filtered_and_joined(
    testing_app: 'TestClient',
    db_session: 'AsyncSession',
    test_related_model_factory: 'TestRelatedModelFactoryProtocol',
    test_base_model_list_factory: 'TestBaseModelListFactoryProtocol',
) -> None:
    """Проверка получения количества записей в базе с фильтрацией и объединениями."""
    repo = TestRepository(db_session)
    items = await test_base_model_list_factory(count=2, disabled_at=None)
    assert len(items) == 2
    item = items[0]
    for item in items:
        assert item.disabled_at is None
    await test_related_model_factory(test_base_model_id=item.id, disabled_at=None)
    disabled_items = await test_base_model_list_factory(
        count=2,
        disabled_at=fake_datetimes.datetime(),
    )
    assert len(disabled_items) == 2
    disabled_item = disabled_items[0]
    for disabled_item in disabled_items:
        assert disabled_item.disabled_at is not None
    await test_related_model_factory(
        test_base_model_id=disabled_item.id,
        disabled_at=fake_datetimes.datetime(),
    )
    count = await repo.get_db_items_count(
        joins=((TestRelatedModel, TestRelatedModel.test_base_model_id == TestBaseModel.id),),
        filters=(TestRelatedModel.disabled_at.is_not(None),),
    )
    disabled_count = await repo.get_db_items_count(
        joins=((TestRelatedModel, TestRelatedModel.test_base_model_id == TestBaseModel.id),),
        filters=(TestRelatedModel.disabled_at.is_(None),),
    )
    assert count == 1
    assert disabled_count == 1
