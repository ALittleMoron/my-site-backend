"""Модуль типов данных моделей проекта, связанный с датами и временем."""
import datetime
import zoneinfo
from typing import TYPE_CHECKING, Any

from sqlalchemy import DateTime, TypeDecorator
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql import expression

if TYPE_CHECKING:
    from sqlalchemy import Dialect


UTC = zoneinfo.ZoneInfo('UTC')


class Utcnow(expression.FunctionElement):  # type: ignore
    """Функция-конструкция для sql запросов."""

    type = DateTime()  # noqa: A003


class UTCDateTime(TypeDecorator[datetime.datetime]):
    """Класс-декоратор для DateTime для автоматической подстановки tzinfo=UTC."""

    impl = DateTime(timezone=True)
    cache_ok = True

    def process_result_value(
        self: 'UTCDateTime',
        value: 'datetime.datetime | None',
        dialect: 'Dialect',  # noqa
    ) -> 'datetime.datetime | None':
        """Метод получения поля.

        Добавляет tzinfo=UTC в дату и время значения.
        """
        if isinstance(value, datetime.datetime) and value.tzinfo is None:
            return value.replace(tzinfo=UTC)
        return value

    def process_bind_param(
        self: 'UTCDateTime',
        value: 'datetime.datetime | None',
        dialect: 'Dialect',  # noqa
    ) -> 'datetime.datetime | None':
        """Метод для присваивания поля.

        Ничего не делает, потому что SqlAlchemy автоматически переводит значение в UTC.
        """
        if isinstance(value, datetime.datetime) and value.tzinfo is None:
            return value.replace(tzinfo=UTC)
        return value


@compiles(Utcnow, 'postgresql')
def pg_utcnow(type_: Any, compiler: Any, **kwargs: Any) -> str:  # noqa
    """Маппинг класса Utcnow на функцию в postgresql."""
    return "TIMEZONE('utc', CURRENT_TIMESTAMP)"
