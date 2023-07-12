"""Модуль примесей времени для моделей проекта."""
import datetime

from sqlalchemy.orm import Mapped, MappedColumn, mapped_column

from app.core.models.types.datetime import UTCDateTime, Utcnow


def get_column_created_at() -> MappedColumn[UTCDateTime]:
    """Отдает подготовленное поле, являющееся датой и временем создания.

    Returns
    -------
    Column[UTCDateTime]
        колонка в базе данных.
    """
    return mapped_column(UTCDateTime, server_default=Utcnow())


def get_column_updated_at() -> MappedColumn[UTCDateTime]:
    """Отдает подготовленное поле, являющееся датой и временем последнего обновления.

    Returns
    -------
    Column[UTCDateTime]
        колонка в базе данных.
    """
    return mapped_column(
        UTCDateTime,
        server_default=Utcnow(),
        server_onupdate=Utcnow(),  # type: ignore
    )


class TimeMixin:
    """Примесь, отвечающая за добавление в классы-модели поля времени создания и обновления."""

    created_at: Mapped[datetime.datetime] = get_column_created_at()  # type: ignore
    updated_at: Mapped[datetime.datetime] = get_column_updated_at()  # type: ignore

    @property
    def updated_at_date(self: 'TimeMixin') -> 'datetime.date':
        """Свойство даты обновления сущности.

        Returns
        -------
            date: дата обновления сущности.
        """
        return self.updated_at.date()

    @property
    def created_at_date(self: 'TimeMixin') -> 'datetime.date':
        """Свойство даты создания сущности.

        Returns
        -------
            date: дата создания сущности.
        """
        return self.created_at.date()

    @property
    def updated_at_isoformat(self: 'TimeMixin') -> str:
        """Свойство даты и времени обновления сущности в формате ISO-8601.

        Returns
        -------
            str: дата и время обновления сущности.
        """
        return self.updated_at.isoformat()

    @property
    def created_at_isoformat(self: 'TimeMixin') -> str:
        """Свойство даты и времени создания сущности в формате ISO-8601.

        Returns
        -------
            str: дата и время создания сущности.
        """
        return self.created_at.isoformat()
