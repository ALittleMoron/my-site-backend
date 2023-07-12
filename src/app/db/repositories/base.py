"""Модуль базового абстрактного репозитория."""
import enum
from typing import TYPE_CHECKING, Any, Generic, Literal, TypeVar

from app.core.exceptions import repositories as repository_exceptions
from app.db.queries.base import BaseQuery

if TYPE_CHECKING:
    from collections.abc import Sequence
    from uuid import UUID

    from pydantic import BaseModel
    from sqlalchemy.ext.asyncio import AsyncSession
    from sqlalchemy.orm.attributes import InstrumentedAttribute
    from sqlalchemy.orm.strategy_options import _AbstractLoad  # type: ignore
    from sqlalchemy.sql.elements import ColumnElement
    from sqlalchemy.sql.functions import Function

    from app.core.models.tables.base import Base

    Identity = str | int | UUID
    JoinKwargs = dict[str, Any]
    Model = type[Base]
    JoinClause = ColumnElement[bool]
    ModelWithOnclause = tuple[Model, JoinClause]
    CompleteModel = tuple[Model, JoinClause, JoinKwargs]
    Join = Model | ModelWithOnclause | CompleteModel


BaseSQLAlchemyModel = TypeVar('BaseSQLAlchemyModel', bound='Base')


MODEL_INCORRECT_STATE_MESSAGE_TEMPLATE = (
    'Ошибка подготовки запрос: модель данных параметра model (значение {model_class}) '
    'конфликтует с моделью по умолчанию {default_model_class}. Возможно, '
    'не была передана модель model вместе с тем, как атрибут класса model_class тоже '
    'тоже не был установлен. Убедитесь, что вы не удалили атрибут model_class перед '
    'вызовом метода отправки запроса в базу, либо передайте параметр model явно.'
)


class SelectModeEnum(str, enum.Enum):
    """Enum режимов получения данных вместе со связанными сущностями.

    Определяет то, будут ли произведены join'ы и options, или нет.
    """

    BRIEF = 'brief'
    VERBOSE = 'verbose'


class BaseRepository(Generic[BaseSQLAlchemyModel]):
    """Абстрактный базовый класс для репозиториев."""

    model_class: type['BaseSQLAlchemyModel']

    def __init__(
        self: "BaseRepository[BaseSQLAlchemyModel]",
        session: 'AsyncSession',
    ) -> None:
        """Экземпляр дочернего класса от абстрактного базового репозитория.

        Parameters
        ----------
        session
            сессия `sqlalchemy`.
        """
        self.session = session
        self.base_queries = BaseQuery(session)

    def __init_subclass__(cls: type['BaseRepository[BaseSQLAlchemyModel]']) -> None:
        """Проверка инициализации нужный атрибутов у дочерних классов."""
        if not hasattr(cls, 'model_class'):
            msg = (
                f'Дочерний класс {cls.__name__} базового класса BaseRepository должен '
                f'имплементировать классовый атрибут "model_class" для работы методов.'
            )
            raise repository_exceptions.RepositorySubclassNotSetAttributeError(msg)

    @property
    def visibility_filters(
        self: 'BaseRepository[BaseSQLAlchemyModel]',
    ) -> 'tuple[ColumnElement[bool], ...]':
        """Выдает фильтры для контроля видимости сущностей."""
        raise NotImplementedError()

    async def _get_item(
        self: "BaseRepository[BaseSQLAlchemyModel]",
        *,
        item_identity: 'Identity',
        item_identity_field: str = 'id',
        model: type['BaseSQLAlchemyModel'] | None = None,
        joins: 'Sequence[Join] | None' = None,
        options: 'Sequence[_AbstractLoad] | None' = None,
        select_mode: SelectModeEnum = SelectModeEnum.BRIEF,
    ) -> 'BaseSQLAlchemyModel | None':
        """Базовый метод репозитория получения записи из БД по id.

        Parameters
        ----------
        model
            модель данных sqlalchemy.
        item_identity
            идентификатор для фильтрации.
        item_identity_field
            название поля для фильтрации (Default: ``'id'``).
        joins
            sql-join'ы (Default: ``None``).
        options
            стратегии объединения (subquery, lazy, join, etc.) данных (Default: ``None``).
        select_mode
            режим получения данных (Default: ``SelectModeEnum.BRIEF``).

        Returns
        -------
        BaseSQLAlchemyModel | None
            либо экземпляр модели sqlalchemy, либо None.

        Raises
        ------
        ValueError
            если в ``search_by`` были переданы или если поле ``item_identity_field`` не присутствует
            в модели ``model``.
        """
        if select_mode == SelectModeEnum.BRIEF:
            joins = None
            options = None
        result = await self.base_queries.get_db_item(
            model=model or self.model_class,
            item_identity=item_identity,
            item_identity_field=item_identity_field,
            joins=joins,
            options=options,
        )
        return result

    async def _get_db_items_count(
        self: "BaseRepository[BaseSQLAlchemyModel]",
        *,
        model: type['BaseSQLAlchemyModel'] | None = None,
        joins: 'Sequence[Join] | None' = None,
        filters: 'Sequence[ColumnElement[bool]] | None' = None,
    ) -> int:
        """Получение количество записей в БД.

        Parameters
        ----------
        model
            модель данных sqlalchemy.
        joins
            sql-join'ы (Default: ``None``).
        filters
            фильтры запроса (Default: ``None``).

        Returns
        -------
        int
            Количество записей в базе данных по переданной сущности и доп. параметрам.
        """
        result = await self.base_queries.get_db_items_count(
            model=model or self.model_class,
            joins=joins,
            filters=filters,
        )
        return result

    async def _get_item_list(
        self: "BaseRepository[BaseSQLAlchemyModel]",
        *,
        model: type['BaseSQLAlchemyModel'] | None = None,
        joins: 'Sequence[Join] | None' = None,
        options: 'Sequence[_AbstractLoad] | None' = None,
        filters: 'Sequence[ColumnElement[bool]] | None' = None,
        search: str | None = None,
        search_by: 'Sequence[str | InstrumentedAttribute[Any] | Function[Any]] | None' = None,
        order_by: 'Sequence[str | ColumnElement[Any] | InstrumentedAttribute[Any]] | None' = None,
        limit: int | None = None,
        offset: int | None = None,
        select_mode: SelectModeEnum = SelectModeEnum.BRIEF,
    ) -> 'Sequence[BaseSQLAlchemyModel]':
        """Базовый метод репозитория получение списка записей из БД.

        Parameters
        ----------
        model
            модель данных sqlalchemy.
        joins
            sql-join'ы (Default: ``None``).
        options
            стратегии объединения (subquery, lazy, join, etc.) данных (Default: ``None``).
        filters
            фильтры запроса (Default: ``None``).
        search
            значение для поиска (Default: ``None``).
        search_by
            поля для поиска (Default: ``None``).
        order_by
            поля для сортировки
        limit
            ограничение по количеству записей (Default: ``None``).
        offset
            сдвиг по итоговой последовательности записей (Default: ``None``).
        select_mode
            режим получения данных (Default: ``SelectModeEnum.BRIEF``).

        Returns
        -------
        Sequence[BaseSQLAlchemyModel]
            последовательность (список) экземпляров модели SQLAlchemy.
        """
        if select_mode == SelectModeEnum.BRIEF:
            joins = None
            options = None
        result = await self.base_queries.get_db_item_list(
            model=model or self.model_class,
            joins=joins,
            options=options,
            filters=filters,
            search=search,
            search_by=search_by,
            order_by=order_by,
            limit=limit,
            offset=offset,
        )
        return result

    async def _create_item(
        self: 'BaseRepository[BaseSQLAlchemyModel]',
        *,
        model: type['BaseSQLAlchemyModel'] | None = None,
        data: 'BaseModel | dict[str, Any] | None' = None,
        use_flush: bool = False,
    ) -> 'BaseSQLAlchemyModel':
        """Базовый метод репозитория создания записи в БД.

        Parameters
        ----------
        model
            модель данных sqlalchemy.
        data
            данные для создания экземпляра модели.
        use_flush
            использовать ли ``.flush()`` у сессии вместо ``.commit()``? По умолчанию False.

        Returns
        -------
        BaseSQLAlchemyModel
            созданный экземпляр модели sqlalchemy.
        """
        result = await self.base_queries.create_item(
            model=self.model_class,
            data=data,
            use_flush=use_flush,
        )
        return result

    async def change_item(
        self: 'BaseRepository[BaseSQLAlchemyModel]',
        *,
        data: 'BaseModel | dict[str, Any]',
        item: 'BaseSQLAlchemyModel',
        set_none: bool = False,
        allowed_none_fields: 'Literal["*"] | Sequence[str]' = '*',
        use_flush: bool = False,
    ) -> 'tuple[bool, BaseSQLAlchemyModel]':
        """Изменение записи из БД.

        Parameters
        ----------
        model
            модель данных sqlalchemy.
        data
            данные для создания экземпляра модели.
        use_flush
            использовать ли ``.flush()`` у сессии вместо ``.commit()``? По умолчанию False.
        return_is_updated_flag
            возвращать ли результат с флагом обновления данных? По умолчанию False. Флаг говорит,
            были ли изменены данные у текущего `item``'а или нет.

        Returns
        -------
        BaseSQLAlchemyModel
            измененный экземпляр модели sqlalchemy.
        tuple[bool, BaseSQLAlchemyModel]
            флаг обновления сущности и обновленная сущность (экземпляр модели).
        """
        result = await self.base_queries.change_db_item(
            data=data,
            item=item,
            set_none=set_none,
            allowed_none_fields=allowed_none_fields,
            use_flush=use_flush,
        )
        return result
