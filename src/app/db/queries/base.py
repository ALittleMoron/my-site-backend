import datetime
import re
from typing import TYPE_CHECKING, Any, Literal, TypeVar

from sqlalchemy import CursorResult, and_
from sqlalchemy import exc as sqlalchemy_exc
from sqlalchemy import func, or_, select, update

from app.core.config import get_logger
from app.utils import datetime as datetime_utils

if TYPE_CHECKING:
    from collections.abc import Sequence
    from uuid import UUID

    from pydantic import BaseModel
    from sqlalchemy.ext.asyncio import AsyncSession
    from sqlalchemy.orm.attributes import InstrumentedAttribute
    from sqlalchemy.orm.strategy_options import _AbstractLoad  # type: ignore
    from sqlalchemy.sql.elements import ColumnElement
    from sqlalchemy.sql.functions import Function
    from sqlalchemy.sql.selectable import Select

    from app.core.models.tables.base import Base

    BaseSQLAlchemyModel = TypeVar('BaseSQLAlchemyModel', bound=Base)
    BasePydanticModel = TypeVar('BasePydanticModel', bound=BaseModel)
    T = TypeVar('T')
    Same = TypeVar('Same')
    Count = int
    Identity = str | int | UUID
    Deleted = bool
    JoinKwargs = dict[str, Any]
    Model = type[Base]
    JoinClause = ColumnElement[bool]
    ModelWithOnclause = tuple[Model, JoinClause]
    CompleteModel = tuple[Model, JoinClause, JoinKwargs]
    Join = Model | ModelWithOnclause | CompleteModel


logger = get_logger('app')


class BaseQuery:
    """Базовый класс запросов в базу данных."""

    def __init__(self: 'BaseQuery', session: 'AsyncSession') -> None:
        self.session = session

    def _resolve_joins(
        self: 'BaseQuery',
        *,
        stmt: 'Select[tuple[T]]',
        joins: 'Sequence[Join]',
    ) -> 'Select[tuple[T]]':
        """Применяет полученные join'ы к нужному select'у."""
        for join in joins:
            if isinstance(join, tuple | list):
                join_kwargs: dict[Any, Any] = dict()
                right, clause, *kw_list = join
                if len(kw_list) == 1:
                    join_kwargs.update(kw_list[0])
                stmt = stmt.join(right, clause, **join_kwargs)
            else:
                stmt = stmt.join(join)
        return stmt

    def _make_disable_filters(  # noqa: C901
        self: 'BaseQuery',
        *,
        id_field: 'InstrumentedAttribute[Any]',
        ids_to_disable: set[Any],
        disable_field: 'InstrumentedAttribute[Any]',
        field_type: type[datetime.datetime] | type[bool] = datetime.datetime,
        allow_filter_by_value: bool = True,
        extra_filters: 'Sequence[ColumnElement[bool]] | None' = None,
    ) -> list['ColumnElement[bool]']:
        """Формирует фильтры для отключения сущностей в базе данных.

        Parameters
        ----------
        id_field
            поле для фильтрации по таблице.
        ids_to_disable
            множество идентификаторов, по которым будет производиться "отключение".
        disable_field
            поле для дополнительной фильтрации для того, чтобы не перезаписывать уже "отключенные"
            данные.
        field_type
            тип значения для поля, показывающего, что сущность была "отключена".
        allow_filter_by_value
            разрешить фильтрацию по полю disable_field.
        extra_filters
            дополнительные фильтры.

        Returns
        -------
        list[ColumnElement[bool]]
            список фильтров для "отключения" записей в базе данных.
        """
        filters: list['ColumnElement[bool]'] = list()
        filters.append(id_field.in_(ids_to_disable))
        if allow_filter_by_value and field_type == bool:
            filters += (disable_field.is_(False),)  # noqa: FBT003
        elif allow_filter_by_value and field_type == datetime.datetime:
            filters += (disable_field.is_(None),)
        filters.extend(extra_filters or [])
        return filters

    def _make_search_filter(
        self: 'BaseQuery',
        search: str,
        model: type['BaseSQLAlchemyModel'],
        *search_by_args: 'str | InstrumentedAttribute[Any] | Function[Any]',
        use_and_clause: bool = False,
    ) -> 'ColumnElement[bool]':
        """создание фильтра поиска на основании введенных параметров."""
        filters: list['ColumnElement[bool]'] = []
        for search_by in search_by_args:
            if isinstance(search_by, str):
                if not hasattr(model.__table__.columns, search_by):
                    msg = f'{search_by} не является полем модели {model.__name__}'
                    raise ValueError(msg)
                column: 'InstrumentedAttribute[Any]' = getattr(model, search_by)
                clause = column.ilike(f'%{search}%')
                filters.append(clause)
            else:
                filters.append(search_by.ilike(f'%{search}%'))
        if use_and_clause:
            and_(*filters)
        return or_(*filters)

    def _get_item_identity_filter(
        self: 'BaseQuery',
        *,
        model: type['BaseSQLAlchemyModel'],
        item_identity: 'Identity',
        item_identity_field: str = 'id',
    ) -> 'ColumnElement[bool]':
        r"""Конвертирует строку идентификатора в фильтр.

        Parameters
        ----------
        model
            модель данных sqlalchemy.
        item_identity
            идентификатор для фильтрации.
        item_identity_field
            название поля для фильтрации (Default: `'id'`).

        Returns
        -------
        ColumnElement[bool]
            фильтр для запроса в ``session.query(...).filter`` или ``select(...).where``.

        Raises
        ------
        ValueError
            выбрасывается, когда поле не присутствует в модели ``model``.
        """
        if not hasattr(model.__table__.columns, item_identity_field):
            msg = f'{item_identity_field} не является полем модели {model.__name__}'
            raise ValueError(msg)
        column: 'InstrumentedAttribute[Any]' = getattr(model.__table__.columns, item_identity_field)
        return column == item_identity

    async def get_db_item(
        self: 'BaseQuery',
        *,
        model: type['BaseSQLAlchemyModel'],
        item_identity: 'Identity',
        item_identity_field: str = 'id',
        filters: 'Sequence[ColumnElement[bool]] | None' = None,
        joins: 'Sequence[Join] | None' = None,
        options: 'Sequence[_AbstractLoad] | None' = None,
    ) -> 'BaseSQLAlchemyModel | None':
        """Получение записи из БД по id.

        Parameters
        ----------
        model
            модель данных sqlalchemy.
        item_identity
            идентификатор для фильтрации.
        item_identity_field
            название поля для фильтрации (Default: ``'id'``).
        filters
            фильтры запроса (Default: ``None``).
        joins
            sql-join'ы (Default: ``None``).
        options
            стратегии объединения (subquery, lazy, join, etc.) данных (Default: ``None``).

        Returns
        -------
        BaseSQLAlchemyModel | None
            либо экземпляр модели sqlalchemy, либо None

        Raises
        ------
        ValueError
            если в ``search_by`` были переданы или если поле ``item_identity_field`` не присутствует
            в модели ``model``.
        """
        stmt = select(model)
        if joins:
            stmt = self._resolve_joins(stmt=stmt, joins=joins)
        for option in options or []:
            stmt = stmt.options(option)
        _filter = self._get_item_identity_filter(
            model=model,
            item_identity=item_identity,
            item_identity_field=item_identity_field,
        )
        if filters:
            stmt = stmt.where(*filters)
        stmt = stmt.where(_filter)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_db_items_count(
        self: 'BaseQuery',
        *,
        model: type['BaseSQLAlchemyModel'],
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
        stmt = select(func.count()).select_from(model)
        if joins:
            stmt = self._resolve_joins(stmt=stmt, joins=joins)
        if filters:
            stmt = stmt.filter(*filters)
        result = await self.session.execute(stmt)
        count = result.scalar()
        if count is None:
            count = 0
        return count

    async def get_db_item_list(
        self: 'BaseQuery',
        *,
        model: type['BaseSQLAlchemyModel'],
        joins: 'Sequence[Join] | None' = None,
        options: 'Sequence[_AbstractLoad] | None' = None,
        filters: 'Sequence[ColumnElement[bool]] | None' = None,
        search: str | None = None,
        search_by: 'Sequence[str | InstrumentedAttribute[Any] | Function[Any]] | None' = None,
        order_by: 'Sequence[str | ColumnElement[Any] | InstrumentedAttribute[Any]] | None' = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> 'Sequence[BaseSQLAlchemyModel]':
        """Получение списка записей из бд.

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

        Returns
        -------
        Sequence[BaseSQLAlchemyModel]
            последовательность (список) экземпляров модели SQLAlchemy.
        """
        stmt = select(model)
        if search and search_by:
            search = re.escape(search)
            search = search.translate(str.maketrans({'%': r'\%', '_': r'\_', '/': r'\/'}))
            stmt = stmt.where(self._make_search_filter(search, model, *search_by))
        if joins:
            stmt = self._resolve_joins(stmt=stmt, joins=joins)
        for option in options or []:
            stmt = stmt.options(option)
        if filters:
            stmt = stmt.where(*filters)
        if order_by is not None:
            stmt = stmt.order_by(*order_by)
        if isinstance(limit, int):
            stmt = stmt.limit(limit)
        if isinstance(offset, int):
            stmt = stmt.offset(offset)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def create_item(
        self: 'BaseQuery',
        *,
        model: type['BaseSQLAlchemyModel'],
        data: 'BaseModel | dict[str, Any] | None' = None,
        use_flush: bool = False,
    ) -> 'BaseSQLAlchemyModel':
        """Создание записи из БД.

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
        if data is None:
            item = model()
        elif isinstance(data, dict):
            item = model(**data)
        else:
            item = model(**data.model_dump())
        self.session.add(item)
        if use_flush:
            await self.session.flush()
        else:
            await self.session.commit()

        logger.debug(
            'Создание в БД: успешное создание. Экземпляр: %s. %s.',
            item,
            'Создание без фиксирования.' if use_flush else 'Создание и фиксирование.',
        )
        return item

    async def change_db_item(
        self: 'BaseQuery',
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
        data
            данные для обновления экземпляра модели.
        item
            экземпляр модели.
        set_none
            флаг, указывающий то, нужно ли устанавливать None в значение.
        allowed_none_fields
        use_flush
            использовать ли ``.flush()`` у сессии вместо ``.commit()``? По умолчанию False.

        Returns
        -------
        BaseSQLAlchemyModel
            измененный экземпляр модели sqlalchemy.
        tuple[bool, BaseSQLAlchemyModel]
            флаг обновления сущности и обновленная сущность (экземпляр модели).
        """
        is_updated = False
        params = data if isinstance(data, dict) else data.model_dump()
        if not set_none:
            params = {key: value for key, value in params.items() if value is not None}
        for field, value in params.items():
            if (
                set_none
                and value is None
                and (allowed_none_fields != '*' and field not in allowed_none_fields)
            ):
                continue
            if not is_updated and getattr(item, field, None) != value:
                is_updated = True
            setattr(item, field, value)
        if use_flush:
            await self.session.flush()
        else:
            await self.session.commit()
        logger.debug(
            (
                'Обновление строки БД: успешное обновление. Экземпляр: %r. Параметры: %s, '
                'set_none: %s, use_flush: %s.'
            ),
            *(item, params, set_none, use_flush),
        )
        return is_updated, item

    async def delete_db_item(
        self: 'BaseQuery',
        *,
        item: 'Base',
        use_flush: bool = False,
    ) -> 'Deleted':
        """Удаление записи из БД.

        Parameters
        ----------
        item
            экземпляр модели sqlalchemy.
        use_flush
            использовать ли ``.flush()`` у сессии вместо ``.commit()``? По умолчанию False.

        Returns
        -------
        bool
            был ли экземпляр удалён из базы?
        """
        item_repr = repr(item)
        try:
            await self.session.delete(item)
            if use_flush:
                await self.session.flush()
            else:
                await self.session.commit()
        except sqlalchemy_exc.SQLAlchemyError as exc:
            await self.session.rollback()
            logger.warning('Удаление из БД: ошибка удаления: %s', exc)
            return False
        logger.debug('Удаление из БД: успешное удаление. Экземпляр: %s', item_repr)
        return True

    async def disable_db_items(
        self: 'BaseQuery',
        *,
        model: type['BaseSQLAlchemyModel'],
        ids_to_disable: set[Any],
        id_field: 'InstrumentedAttribute[Any]',
        disable_field: 'InstrumentedAttribute[Any]',
        field_type: type[datetime.datetime] | type[bool] = datetime.datetime,
        allow_filter_by_value: bool = True,
        extra_filters: 'Sequence[ColumnElement[bool]] | None' = None,
        use_flush: bool = False,
    ) -> 'Count':
        """Отключает записи в базе данных (устанавливают нужное значение выбранному полю).

        Parameters
        ----------
        model
            модель данных sqlalchemy.
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

        Returns
        -------
        int
            количество "отключенных" записей.

        Raises
        ------
        TypeError
            в случае, если был передан невалидный field_type.
        AttributeError
            в случае ошибки создания фильтров для отключения.
        """
        if issubclass(field_type, bool):
            field_value = True
        elif issubclass(field_type, datetime.datetime):  # type: ignore
            field_value = datetime_utils.get_utc_now()
        else:
            msg = (
                f'Параметр "field_type" должен быть одним из следующих: bool, datetime. '
                f'Был передан {field_type}.'
            )
            raise TypeError(msg)
        if not ids_to_disable:
            return 0
        try:
            filters = self._make_disable_filters(
                ids_to_disable=ids_to_disable,
                id_field=id_field,
                disable_field=disable_field,
                field_type=field_type,
                allow_filter_by_value=allow_filter_by_value,
                extra_filters=extra_filters,
            )
        except AttributeError:
            params = dict(
                ids_to_disable=ids_to_disable,
                id_field=id_field,
                disable_field=disable_field,
                field_type=field_type,
                allow_filter_by_value=allow_filter_by_value,
                extra_filters=extra_filters,
            )
            logger.exception(
                'Ошибка создания фильтров для отключения сущностей в базе данных. Параметры: %s.',
                params,
            )
            return 0
        stmt = update(model).where(*filters).values({disable_field: field_value})
        result = await self.session.execute(stmt)
        if use_flush:
            await self.session.flush()
        else:
            await self.session.commit()
        # только в CursorResult есть атрибут rowcount
        if isinstance(result, CursorResult):
            return result.rowcount
        # не получится узнать реальное количество измененных сущностей. Поэтому 0.
        return 0
