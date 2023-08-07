import datetime
from typing import TYPE_CHECKING, Any, Protocol
from zoneinfo import ZoneInfo

import freezegun
import pytest
from mimesis import Datetime, Locale, Text
from sqlalchemy.orm import joinedload

from app.core.exceptions.repositories import RepositorySubclassNotSetAttributeError
from app.core.models.tables.tests import Base, TestBaseModel, TestRelatedModel
from app.core.schemas.classes.tests import TestBaseCreateModel, TestBaseUpdateModel
from app.db.queries.base import BaseQuery
from app.db.repositories.base import BaseRepository, SelectModeEnum

if TYPE_CHECKING:
    import uuid
    from collections.abc import Awaitable

    from fastapi.testclient import TestClient
    from sqlalchemy.ext.asyncio import AsyncSession
    from sqlalchemy.sql.elements import ColumnElement

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


fake_datetimes = Datetime(Locale.RU)
fake_text = Text(Locale.RU)


class TestRepository(BaseRepository[TestBaseModel, BaseQuery]):
    """Тестовый репозиторий."""

    __test__ = False
    model_class = TestBaseModel
    query_class = BaseQuery


def test_base_query_item_identity_error(
    testing_app: 'TestClient',
    db_session: 'AsyncSession',
) -> None:
    """Проверка передачи невалидного item_identity_field.."""
    repo = TestRepository(db_session)
    with pytest.raises(ValueError, match='abc не является полем модели TestBaseModel'):
        repo.queries._get_item_identity_filter(  # type: ignore
            model=TestBaseModel,
            item_identity=25,
            item_identity_field="abc",
        )


def test_repository_model_class_attribute_error() -> None:
    """Проверка выбрасывания ошибки при попытке создать репозиторий без model_class."""
    with pytest.raises(RepositorySubclassNotSetAttributeError):

        class TestFailRepository(BaseRepository):  # type: ignore
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
    received_item = await repo.get(item_identity=item.id)
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
    received_item = await repo.get(
        item_identity=item.id,
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
    received_items = await repo.list()
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
    count = await repo.count()  # type: ignore
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
    count = await repo.count(
        filters=(TestBaseModel.disabled_at.is_not(None),),
    )
    disabled_count = await repo.count(
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
    count = await repo.count(
        joins=((TestRelatedModel, TestRelatedModel.test_base_model_id == TestBaseModel.id),),
        filters=(TestRelatedModel.disabled_at.is_not(None),),
    )
    disabled_count = await repo.count(
        joins=((TestRelatedModel, TestRelatedModel.test_base_model_id == TestBaseModel.id),),
        filters=(TestRelatedModel.disabled_at.is_(None),),
    )
    assert count == 1
    assert disabled_count == 1


@pytest.mark.asyncio()
async def test_create_item(
    testing_app: 'TestClient',
    db_session: 'AsyncSession',
) -> None:
    """Проверка создания сущности."""
    repo = TestRepository(db_session)
    create_data = TestBaseCreateModel(
        text=fake_text.text(5),
        disabled_at=fake_datetimes.datetime(),
    )
    new_item = await repo.create(data=create_data)
    assert new_item.id is not None
    assert new_item.text == create_data.text
    assert new_item.disabled_at == create_data.disabled_at


@pytest.mark.asyncio()
async def test_update_item(
    testing_app: 'TestClient',
    db_session: 'AsyncSession',
    test_base_model_factory: 'TestBaseModelFactoryProtocol',
) -> None:
    """Проверка создания сущности."""
    utc = ZoneInfo('UTC')
    now = datetime.datetime.now(tz=utc)
    some_future = now + datetime.timedelta(days=2)
    repo = TestRepository(db_session)
    item = await test_base_model_factory(text='some text', disabled_at=now)
    item_text = item.text
    item_disabled_at = item.disabled_at
    update_data = TestBaseUpdateModel(
        text=fake_text.text(5),
        disabled_at=fake_datetimes.datetime().replace(tzinfo=utc),
    )
    with freezegun.freeze_time(some_future):
        updated, new_item = await repo.update(data=update_data, item=item)
    assert updated, 'Не обновлён'
    assert new_item.id == item.id
    assert new_item.text == update_data.text
    assert new_item.text != item_text
    assert new_item.disabled_at is not None
    assert new_item.disabled_at.replace(tzinfo=utc) == update_data.disabled_at
    assert new_item.disabled_at.replace(tzinfo=utc) != item_disabled_at


@pytest.mark.asyncio()
async def test_disable_items(
    testing_app: 'TestClient',
    db_session: 'AsyncSession',
    test_base_model_factory: 'TestBaseModelFactoryProtocol',
) -> None:
    """Проверка отключения сущности."""
    utc = ZoneInfo('UTC')
    now = datetime.datetime.now(tz=utc)
    some_future = now + datetime.timedelta(days=2)
    repo = TestRepository(db_session)
    item = await test_base_model_factory(text='some text', disabled_at=None)
    with freezegun.freeze_time(some_future):
        count = await repo.disable(
            ids_to_disable={item.id},
            id_field=TestBaseModel.id,
            disable_field=TestBaseModel.disabled_at,
        )
    assert count == 1
    item = await repo.get(item_identity=item.id)
    assert item is not None
    assert item.disabled_at is not None
    assert item.disabled_at == some_future
