"""Модуль базового абстрактного репозитория."""
import datetime
import enum
from typing import TYPE_CHECKING, Any, Generic, Literal, TypeVar, get_args

from app.core.config import get_logger
from app.core.exceptions import repositories as repository_exceptions
from app.core.models.tables.base import Base
from app.db.mixins.permissions import PermissionMixin, PermissionModeEnum
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

    Schema = TypeVar('Schema', bound=BaseModel)

    JoinRequired = bool
    Count = int
    Identity = str | int | UUID
    JoinKwargs = dict[str, Any]
    Model = type[Base]
    JoinClause = ColumnElement[bool]
    ModelWithOnclause = tuple[Model, JoinClause]
    CompleteModel = tuple[Model, JoinClause, JoinKwargs]
    Join = Model | ModelWithOnclause | CompleteModel


logger = get_logger('app')
BaseSQLAlchemyModel = TypeVar('BaseSQLAlchemyModel', bound=Base)
Query = TypeVar('Query', bound=BaseQuery)


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


class BaseRepository(Generic[BaseSQLAlchemyModel, Query], PermissionMixin):
    """Абстрактный базовый класс для репозиториев."""

    model_class: type['BaseSQLAlchemyModel']
    query_class: type['Query']
    specific_column_mapping: 'dict[str, ColumnElement[Any]]' = {}

    def __init__(
        self: 'BaseRepository[BaseSQLAlchemyModel, Query]',
        session: 'AsyncSession',
    ) -> None:
        """Экземпляр дочернего класса от абстрактного базового репозитория.

        Parameters
        ----------
        session
            сессия `sqlalchemy`.
        """
        self.session = session
        self.queries = self.query_class(session)

    def __init_subclass__(cls) -> None:  # noqa: ANN101
        """Проверка инициализации нужный атрибутов у дочерних классов."""
        base_msg = (
            'При наследовании от базового класса BaseRepository нужно обязательно указывать '
            'GenericType в виде модели и запроса (query).'
        )
        if not hasattr(cls, 'model_class'):
            try:
                # PEP-560: https://peps.python.org/pep-0560/
                # NOTE: тут код получает тип, прокинутый в Generic при наследовании от базового
                #       репозитория, и устанавливает его для model_class.
                # get_args достает прокинутые параметры из __orig_bases__, который хранит информацию
                # о Generic'ах.
                model, query = get_args(cls.__orig_bases__[0])  # type: ignore
                if isinstance(model, TypeVar):
                    msg = f'{base_msg} Не был передан GenericType для модели.'
                    raise TypeError(msg)  # noqa: TRY301
                if isinstance(query, TypeVar):
                    msg = f'{base_msg} Не был передан GenericType для запроса.'
                    raise TypeError(msg)  # noqa: TRY301
                if not issubclass(model, Base):
                    msg = f'{base_msg} Переданный GenericType не является моделью SQLAlchemy.'
                    raise TypeError(msg)  # noqa: TRY301
                if not issubclass(query, BaseQuery):
                    msg = f'{base_msg} Переданный GenericType не является моделью SQLAlchemy.'
                    raise TypeError(msg)  # noqa: TRY301
                cls.model_class = model  # type: ignore
                cls.query_class = query  # type: ignore
            except Exception as exc:
                msg = f'Ошибка атрибута model_class или query_class для {cls.__name__}.'
                raise repository_exceptions.RepositorySubclassNotSetAttributeError(msg) from exc

    async def get(
        self: 'BaseRepository[BaseSQLAlchemyModel, Query]',
        *,
        item_identity: 'Identity',
        item_identity_field: str = 'id',
        extra_filters: 'Sequence[ColumnElement[bool]] | None' = None,
        joins: 'Sequence[Join] | None' = None,
        options: 'Sequence[_AbstractLoad] | None' = None,
        select_mode: SelectModeEnum = SelectModeEnum.BRIEF,
        permission_mode: PermissionModeEnum = PermissionModeEnum.ANYONE,
        ignore_permissions: bool = False,
    ) -> 'BaseSQLAlchemyModel | None':
        """Базовый метод репозитория получения записи из БД по id.

        Parameters
        ----------
        item_identity
            идентификатор для фильтрации.
        item_identity_field
            название поля для фильтрации (Default: ``'id'``).
        extra_filters
            Дополнительные фильтры запроса (Default: ``None``).
        joins
            sql-join'ы (Default: ``None``).
        options
            стратегии объединения (subquery, lazy, join, etc.) данных (Default: ``None``).
        select_mode
            режим получения данных (Default: ``SelectModeEnum.BRIEF``).
        permission_mode
            режим доступа к ресурсу.
        ignore_permissions
            не производить проверку доступа?

        Returns
        -------
        BaseSQLAlchemyModel | None
            либо экземпляр модели sqlalchemy, либо None.
        """
        join_required, filters = self.get_visibility_filter_from_permission(
            method_name='read_detail',
            mode=permission_mode,
            ignore_permissions=ignore_permissions,
            ignore_method_name='get',
        )
        if select_mode == SelectModeEnum.BRIEF:
            if join_required:
                filters = ()
            joins = None
            options = None
        if extra_filters:
            filters += tuple(extra_filters)
        result = await self.queries.get_db_item(
            model=self.model_class,
            item_identity=item_identity,
            item_identity_field=item_identity_field,
            joins=joins,
            options=options,
            filters=filters,
        )
        return result

    async def count(
        self: 'BaseRepository[BaseSQLAlchemyModel, Query]',
        *,
        joins: 'Sequence[Join] | None' = None,
        filters: 'Sequence[ColumnElement[bool]] | None' = None,
        permission_mode: PermissionModeEnum = PermissionModeEnum.ANYONE,
        ignore_permissions: bool = False,
    ) -> int:
        """Получение количество записей в БД.

        Parameters
        ----------
        joins
            sql-join'ы (Default: ``None``).
        filters
            фильтры запроса (Default: ``None``).
        permission_mode
            режим доступа к ресурсу.
        ignore_permissions
            не производить проверку доступа?

        Returns
        -------
        int
            Количество записей в базе данных по переданной сущности и доп. параметрам.
        """
        join_required, _filters = self.get_visibility_filter_from_permission(
            method_name='read_count',
            mode=permission_mode,
            ignore_permissions=ignore_permissions,
            ignore_method_name='count',
        )
        if join_required and not joins:
            _filters = ()
        filters = tuple(filters) if filters else ()
        filters += _filters
        result = await self.queries.get_db_items_count(
            model=self.model_class,
            joins=joins,
            filters=filters,
        )
        return result

    async def list(  # noqa: A003
        self: 'BaseRepository[BaseSQLAlchemyModel, Query]',
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
        permission_mode: PermissionModeEnum = PermissionModeEnum.ANYONE,
        ignore_permissions: bool = False,
    ) -> 'Sequence[BaseSQLAlchemyModel]':
        """Базовый метод репозитория получение списка записей из БД.

        Parameters
        ----------
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
        permission_mode
            режим доступа к ресурсу.
        ignore_permissions
            не производить проверку доступа?

        Returns
        -------
        Sequence[BaseSQLAlchemyModel]
            последовательность (список) экземпляров модели SQLAlchemy.

        Raises
        ------
        ValueError
            если в ``search_by`` были переданы или если поле ``item_identity_field`` не присутствует
            в модели ``model``.
        """
        join_required, _filters = self.get_visibility_filter_from_permission(
            method_name='read_list',
            mode=permission_mode,
            ignore_permissions=ignore_permissions,
            ignore_method_name='list',
        )
        if join_required and not joins:
            _filters = ()
        filters = tuple(filters) if filters else ()
        filters += _filters
        if select_mode == SelectModeEnum.BRIEF:
            joins = None
            options = None
        result = await self.queries.get_db_item_list(
            model=self.model_class,
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

    async def create(
        self: 'BaseRepository[BaseSQLAlchemyModel, Query]',
        *,
        data: 'BaseModel | dict[str, Any] | None' = None,
        use_flush: bool = False,
        permission_mode: PermissionModeEnum = PermissionModeEnum.ANYONE,
        ignore_permissions: bool = False,
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
        permission_mode
            режим доступа к ресурсу.
        ignore_permissions
            не производить проверку доступа?

        Returns
        -------
        BaseSQLAlchemyModel
            созданный экземпляр модели sqlalchemy.
        """
        self.check_permissions(
            method_name='create',
            mode=permission_mode,
            ignore_permissions=ignore_permissions,
            ignore_method_name='create',
        )
        result = await self.queries.create_item(
            model=self.model_class,
            data=data,
            use_flush=use_flush,
        )
        return result

    async def update(
        self: 'BaseRepository[BaseSQLAlchemyModel, Query]',
        *,
        data: 'BaseModel | dict[str, Any]',
        item: 'BaseSQLAlchemyModel',
        set_none: bool = False,
        allowed_none_fields: 'Literal["*"] | Sequence[str]' = '*',
        use_flush: bool = False,
        permission_mode: PermissionModeEnum = PermissionModeEnum.ANYONE,
        ignore_permissions: bool = False,
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
        permission_mode
            режим доступа к ресурсу.
        ignore_permissions
            не производить проверку доступа?

        Returns
        -------
        BaseSQLAlchemyModel
            измененный экземпляр модели sqlalchemy.
        tuple[bool, BaseSQLAlchemyModel]
            флаг обновления сущности и обновленная сущность (экземпляр модели).
        """
        self.check_permissions(
            method_name='update',
            mode=permission_mode,
            ignore_permissions=ignore_permissions,
            ignore_method_name='update',
        )
        result = await self.queries.change_db_item(
            data=data,
            item=item,
            set_none=set_none,
            allowed_none_fields=allowed_none_fields,
            use_flush=use_flush,
        )
        return result

    async def disable(
        self: 'BaseRepository[BaseSQLAlchemyModel, Query]',
        *,
        ids_to_disable: set[Any],
        id_field: 'InstrumentedAttribute[Any]',
        disable_field: 'InstrumentedAttribute[Any]',
        field_type: type[datetime.datetime] | type[bool] = datetime.datetime,
        allow_filter_by_value: bool = True,
        extra_filters: 'Sequence[ColumnElement[bool]] | None' = None,
        use_flush: bool = False,
        permission_mode: PermissionModeEnum = PermissionModeEnum.ANYONE,
        ignore_permissions: bool = False,
    ) -> 'Count':
        """Отключает записи в базе данных (устанавливают нужное значение выбранному полю).

        Parameters
        ----------
        ids_to_disable
            множество идентификаторов, по которым будет производиться "отключение".
        id_field
            поле для фильтрации по таблице.
        disable_field
            поле для дополнительной фильтрации для того, чтобы не перезаписывать уже "отключенные"
            данные.
        field_type
            тип значения для поля, показывающего, что сущность была "отключена".
        allow_filter_by_value
            разрешить фильтрацию по полю disable_field.
        extra_filters
            дополнительные фильтры.
        use_flush
            использовать ли ``.flush()`` у сессии вместо ``.commit()``? По умолчанию False.
        permission_mode
            режим доступа к ресурсу.
        ignore_permissions
            не производить проверку доступа?

        Returns
        -------
        int
            количество "отключенных" записей.
        """
        self.check_permissions(
            method_name='disable',
            mode=permission_mode,
            ignore_permissions=ignore_permissions,
            ignore_method_name='disable',
        )
        result = await self.queries.disable_db_items(
            model=self.model_class,
            ids_to_disable=ids_to_disable,
            id_field=id_field,
            disable_field=disable_field,
            field_type=field_type,
            allow_filter_by_value=allow_filter_by_value,
            extra_filters=extra_filters,
            use_flush=use_flush,
        )
        return result
