import uuid
from typing import TYPE_CHECKING, Any, Protocol

import pytest
from pydantic import BaseModel

from app.core.models.tables.tests import TestBaseModel

if TYPE_CHECKING:
    from collections.abc import Awaitable

    from fastapi.testclient import TestClient
    from sqlalchemy.ext.asyncio import AsyncSession
    from sqlalchemy.sql.elements import ColumnElement

    from app.core.models.tables.tests import Base, TestRelatedModel

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


@pytest.mark.asyncio()
async def test_empty_as_dict_with_no_params(
    testing_app: 'TestClient',
    db_session: 'AsyncSession',
    test_base_model_factory: 'TestBaseModelFactoryProtocol',
) -> None:
    """Проверка пустого словаря без дополнительных параметров."""
    item = await test_base_model_factory()
    item.default_include_fields = None
    item.default_replace_fields = None
    assert item.as_dict() == {}


@pytest.mark.asyncio()
async def test_as_dict_with_default_params(
    testing_app: 'TestClient',
    db_session: 'AsyncSession',
    test_base_model_factory: 'TestBaseModelFactoryProtocol',
) -> None:
    """Проверка словаря с установленными параметрами по умолчанию."""
    item = await test_base_model_factory()
    item.default_include_fields = {'id'}
    item.default_replace_fields = {'aliased_text': 'text'}
    assert item.as_dict() == {'id': item.id, 'aliased_text': item.text}


@pytest.mark.asyncio()
async def test_as_dict_with_passed_params(
    testing_app: 'TestClient',
    db_session: 'AsyncSession',
    test_base_model_factory: 'TestBaseModelFactoryProtocol',
) -> None:
    """Проверка словаря с переданными параметрами."""
    item = await test_base_model_factory()
    item.default_include_fields = None
    item.default_replace_fields = None
    assert item.as_dict('id', aliased_text='text') == {'id': item.id, 'aliased_text': item.text}


@pytest.mark.asyncio()
async def test_as_dict_attribute_not_found_as_none(
    testing_app: 'TestClient',
    db_session: 'AsyncSession',
    test_base_model_factory: 'TestBaseModelFactoryProtocol',
) -> None:
    """Проверка словаря: атрибут не найден - None."""
    item = await test_base_model_factory()
    item.default_include_fields = None
    item.default_replace_fields = None
    assert item.as_dict(aliased_text='text_not_in_model') == {'aliased_text': None}


@pytest.mark.asyncio()
async def test_as_dict_attribute_callable(
    testing_app: 'TestClient',
    db_session: 'AsyncSession',
    test_base_model_factory: 'TestBaseModelFactoryProtocol',
) -> None:
    """Проверка словаря: атрибут - функция."""
    item = await test_base_model_factory()
    item.default_include_fields = None
    item.default_replace_fields = None
    assert item.as_dict(x='some_callable') == {'x': 'abc'}


@pytest.mark.asyncio()
async def test_is_different_from_dict_not_differ(
    testing_app: 'TestClient',
    db_session: 'AsyncSession',
    test_base_model_factory: 'TestBaseModelFactoryProtocol',
) -> None:
    """Проверка разницы модели со словарём: не различимы."""
    item = await test_base_model_factory()
    item.differ_include_fields = None
    assert item.is_different_from({'id': item.id}) is False


@pytest.mark.asyncio()
async def test_is_different_from_dict_differ(
    testing_app: 'TestClient',
    db_session: 'AsyncSession',
    test_base_model_factory: 'TestBaseModelFactoryProtocol',
) -> None:
    """Проверка разницы модели со словарём: разные."""
    item = await test_base_model_factory()
    item.differ_include_fields = None
    assert item.is_different_from({'id': uuid.uuid4()}) is True


@pytest.mark.asyncio()
async def test_is_different_from_dict_include_fields(
    testing_app: 'TestClient',
    db_session: 'AsyncSession',
    test_base_model_factory: 'TestBaseModelFactoryProtocol',
) -> None:
    """Проверка разницы модели со словарём: include поля."""
    item = await test_base_model_factory()
    item.differ_include_fields = {'id'}
    assert item.is_different_from({'id': uuid.uuid4(), 'text': 'test'}) is True


@pytest.mark.asyncio()
async def test_is_different_from_dict_attribute_not_found(
    testing_app: 'TestClient',
    db_session: 'AsyncSession',
    test_base_model_factory: 'TestBaseModelFactoryProtocol',
) -> None:
    """Проверка разницы модели со словарём: атрибут не найден."""
    item = await test_base_model_factory()
    item.differ_include_fields = None
    assert item.is_different_from({'abcde': 'test'}) is True


@pytest.mark.asyncio()
async def test_is_different_from_model_not_differ(
    testing_app: 'TestClient',
    db_session: 'AsyncSession',
    test_base_model_factory: 'TestBaseModelFactoryProtocol',
) -> None:
    """Проверка разницы модели с моделями: не отличаются."""
    item = await test_base_model_factory(text='abc')
    item.differ_include_fields = None
    item_2 = await test_base_model_factory(text='abc')
    item_2.differ_include_fields = None
    assert item.text == item_2.text
    assert (
        item.is_different_from(
            item_2,
            include_fields={
                'text',
            },
        )
        is False
    )


@pytest.mark.asyncio()
async def test_is_different_from_model_differ(
    testing_app: 'TestClient',
    db_session: 'AsyncSession',
    test_base_model_factory: 'TestBaseModelFactoryProtocol',
) -> None:
    """Проверка разницы модели с моделями: отличаются."""
    item = await test_base_model_factory()
    item.differ_include_fields = None
    item_2 = await test_base_model_factory()
    item_2.differ_include_fields = None
    assert item.is_different_from(item_2) is True


@pytest.mark.asyncio()
async def test_is_different_from_model_model_type_differ(
    testing_app: 'TestClient',
    db_session: 'AsyncSession',
    test_base_model_factory: 'TestBaseModelFactoryProtocol',
    test_related_model_factory: 'TestRelatedModelFactoryProtocol',
) -> None:
    """Проверка разницы модели с моделями: отличаются типы данных."""
    item = await test_base_model_factory()
    item.differ_include_fields = None
    item_2 = await test_related_model_factory()
    item_2.differ_include_fields = None
    msg = (
        'Был передан item неправильного типа данных. '
        f'Ожидались: Dict, BaseModel, {item.__class__.__name__}. Пришёл: {type(item_2)}.'
    )
    with pytest.raises(TypeError, match=msg):
        item.is_different_from(item_2)


@pytest.mark.asyncio()
async def test_is_different_from_pydantic_schema_not_differ(
    testing_app: 'TestClient',
    db_session: 'AsyncSession',
    test_base_model_factory: 'TestBaseModelFactoryProtocol',
) -> None:
    """Проверка разницы модели с pydantic-схемой: не отличается."""
    item = await test_base_model_factory(text='abc')
    item.differ_include_fields = None

    class TestPydanticSchema(BaseModel):
        __test__ = False

        text: str | None

    sch = TestPydanticSchema(text=item.text)
    assert (
        item.is_different_from(
            sch,
            include_fields={
                'text',
            },
        )
        is False
    )


@pytest.mark.asyncio()
async def test_is_different_from_pydantic_schema_differ(
    testing_app: 'TestClient',
    db_session: 'AsyncSession',
    test_base_model_factory: 'TestBaseModelFactoryProtocol',
) -> None:
    """Проверка разницы модели с pydantic-схемой: отличается."""
    item = await test_base_model_factory(text='abc')
    item.differ_include_fields = None

    class TestPydanticSchema(BaseModel):
        __test__ = False

        text: str | None

    sch = TestPydanticSchema(text='abcd')
    assert (
        item.is_different_from(
            sch,
            include_fields={'text'},
        )
        is True
    )


@pytest.mark.asyncio()
async def test_model_repr_max_elements(
    testing_app: 'TestClient',
    db_session: 'AsyncSession',
) -> None:
    """Проверка repr модели: максимальное число элементов."""
    item = TestBaseModel(id=25)
    item.max_repr_elements = 1
    assert repr(item) == f'{item.__class__.__name__}(id={item.id})'


@pytest.mark.asyncio()
async def test_model_repr_include_fields(
    testing_app: 'TestClient',
    db_session: 'AsyncSession',
    test_base_model_factory: 'TestBaseModelFactoryProtocol',
) -> None:
    """Проверка repr модели: include полей."""
    item = await test_base_model_factory()
    item.repr_include_fields = {'id', 'text'}
    assert repr(item) == f'{item.__class__.__name__}(id={item.id}, text=\'{item.text}\')'
