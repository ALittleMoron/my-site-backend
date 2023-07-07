"""Модуль базового абстрактного репозитория."""
import enum
from typing import TYPE_CHECKING, Any, TypeVar

from app.db.queries.base import BaseQuery

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
    Identity = str | int | UUID


class SelectModeEnum(str, enum.Enum):
    """Enum режимов получения данных вместе со связанными сущностями.

    Определяет то, будут ли произведены join'ы и options, или нет.
    """

    BRIEF = 'brief'
    VERBOSE = 'verbose'


class BaseRepository:
    """Абстрактный базовый класс для репозиториев."""

    def __init__(self: "BaseRepository", session: 'AsyncSession') -> None:
        """Экземпляр дочернего класса от абстрактного базового репозитория.

        Parameters
        ----------
        session
            сессия `sqlalchemy`.
        """
        self.session = session
        self.base_queries = BaseQuery(session)

    async def _get_item(
        self: "BaseRepository",
        *,
        model: type['BaseSQLAlchemyModel'],
        item_identity: 'Identity',
        item_identity_field: str = 'id',
        joins: 'Sequence[Join]' | None = None,
        options: 'Sequence[_AbstractLoad]' | None = None,
        select_mode: SelectModeEnum = SelectModeEnum.BRIEF,
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
        return await self.base_queries.get_db_item(
            model=model,
            item_identity=item_identity,
            item_identity_field=item_identity_field,
            joins=joins,
            options=options,
        )

    async def _get_item_list(
        self: "BaseRepository",
        *,
        model: type['BaseSQLAlchemyModel'],
        joins: 'Sequence[Join]' | None = None,
        options: 'Sequence[_AbstractLoad]' | None = None,
        filters: 'Sequence[ColumnElement[Any]]' | None = None,
        search: str | None = None,
        search_by: 'Sequence[str | InstrumentedAttribute[Any] | Function[Any]]' | None = None,
        order_by: 'Sequence[str | ColumnElement[Any] | InstrumentedAttribute[Any]]' | None = None,
        limit: int | None = None,  # TODO: поменять на page - per_page схему
        offset: int | None = None,
        select_mode: SelectModeEnum = SelectModeEnum.BRIEF,
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
        return await self.base_queries.get_db_item_list(
            model=model,
            joins=joins,
            options=options,
            filters=filters,
            search=search,
            search_by=search_by,
            order_by=order_by,
            limit=limit,
            offset=offset,
        )

    async def _create_item(
        self: 'BaseRepository',
        *,
        model: type['BaseSQLAlchemyModel'],
    ) -> 'BaseSQLAlchemyModel':
        """"""
        return await self.base_queries
