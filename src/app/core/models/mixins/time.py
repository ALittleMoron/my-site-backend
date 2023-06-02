"""Модуль примесей времени для моделей проекта."""
from typing import TYPE_CHECKING, Any

from sqlalchemy import Column

from app.core.models.types.datetime import UTCDateTime, Utcnow

if TYPE_CHECKING:
    import datetime


def get_column_created_at(**kwargs: Any) -> Column[UTCDateTime]:
    """Отдает подготовленное поле, являющееся датой и временем создания.

    Args:
        **kwargs: доп. параметры.

    Returns:
        Column[UTCDateTime]: колонка в базе данных.
    """
    params = {'server_default': Utcnow()}
    params.update(kwargs)
    return Column(UTCDateTime, **params)


def get_column_updated_at(**kwargs: Any) -> Column[UTCDateTime]:
    """Отдает подготовленное поле, являющееся датой и временем последнего обновления.

    Args:
        **kwargs: доп. параметры.

    Returns:
        Column[UTCDateTime]: колонка в базе данных.
    """
    params = {'server_onupdate': Utcnow(), 'server_default': Utcnow()}
    params.update(kwargs)
    return Column(UTCDateTime, **params)


class TimeMixin:
    """Примесь, отвечающая за добавление в классы-модели поля времени создания и обновления."""

    created_at = get_column_created_at()
    updated_at = get_column_updated_at()

    @property
    def updated_at_date(self) -> 'datetime.date':
        """Свойство даты обновления сущности.

        Returns:
            date: дата обновления сущности.
        """
        return self.updated_at.date()

    @property
    def created_at_date(self) -> 'datetime.date':
        """Свойство даты создания сущности.

        Returns:
            date: дата создания сущности.
        """
        return self.created_at.date()

    @property
    def updated_at_isoformat(self) -> str:
        """Свойство даты и времени обновления сущности в формате ISO-8601.

        Returns:
            str: дата и время обновления сущности.
        """
        return self.updated_at.isoformat()

    @property
    def created_at_isoformat(self) -> str:
        """Свойство даты и времени создания сущности в формате ISO-8601.

        Returns:
            str: дата и время создания сущности.
        """
        return self.created_at.isoformat()
