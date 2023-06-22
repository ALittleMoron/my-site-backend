import re
from typing import TYPE_CHECKING, Any, TypeVar

from sqlalchemy import and_, or_, select

if TYPE_CHECKING:
    from collections.abc import Sequence
    from uuid import UUID

    from sqlalchemy import Join
    from sqlalchemy.ext.asyncio import AsyncSession
    from sqlalchemy.orm.attributes import InstrumentedAttribute
    from sqlalchemy.orm.strategy_options import _AbstractLoad  # type: ignore
    from sqlalchemy.sql.elements import ColumnElement
    from sqlalchemy.sql.functions import Function

    from app.core.models.tables.base import Base

    BaseSQLAlchemyModel = TypeVar('BaseSQLAlchemyModel', bound=Base)
    Count = int
    Identity = str | int | UUID


def _make_search_filter(
    search: str,
    model: type['BaseSQLAlchemyModel'],
    *search_by_args: 'str | InstrumentedAttribute[Any] | Function[Any]',
    use_and_clause: bool = False,
) -> 'ColumnElement[bool]':
    """создание фильтра поиска на основании введенных параметров."""
    filters: 'list[ColumnElement[bool]]' = []
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
    session: 'AsyncSession',
    model: type['BaseSQLAlchemyModel'],
    item_identity: 'Identity',
    item_identity_field: str = 'id',
    joins: 'Sequence[Join]' | None = None,
    options: 'Sequence[_AbstractLoad]' | None = None,
) -> 'BaseSQLAlchemyModel' | None:
    """Получение записи из БД по id.

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
    for join in joins or []:
        stmt = stmt.join(join)
    if options:
        stmt = stmt.options(*options)
    _filter = _get_item_identity_filter(model, item_identity, item_identity_field)
    stmt = stmt.where(_filter)
    result = await session.execute(stmt)
    return result.scalars().first()


async def get_db_item_list(
    session: 'AsyncSession',
    model: type['BaseSQLAlchemyModel'],
    joins: 'Sequence[Join]' | None = None,
    options: 'Sequence[_AbstractLoad]' | None = None,
    filters: 'Sequence[ColumnElement[bool]]' | None = None,
    search: str | None = None,
    search_by: 'Sequence[str | InstrumentedAttribute[Any] | Function[Any]]' | None = None,
    order_by: 'Sequence[str | ColumnElement[Any] | InstrumentedAttribute[Any]]' | None = None,
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
        stmt = stmt.where(_make_search_filter(search, model, *search_by))
    if filters:
        stmt = stmt.where(*filters)
    for join in joins or []:
        stmt = stmt.join(join)
    if options:
        stmt = stmt.options(*options)
    if order_by is not None:
        stmt = stmt.order_by(*order_by)
    if isinstance(limit, int):
        stmt = stmt.limit(limit)
    if isinstance(offset, int):
        stmt = stmt.offset(offset)
    result = await session.execute(stmt)
    return result.scalars().all()
