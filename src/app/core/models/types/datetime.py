"""Модуль типов данных моделей проекта, связанный с датами и временем."""
import datetime
import zoneinfo
from typing import TYPE_CHECKING, Any

from sqlalchemy import DateTime, TypeDecorator
from sqlalchemy.ext.compiler import compiles  # type: ignore
from sqlalchemy.sql import expression

if TYPE_CHECKING:
    from sqlalchemy import Dialect


UTC = zoneinfo.ZoneInfo('UTC')


class Utcnow(expression.FunctionElement):  # type: ignore
    """Функция-конструкция для sql запросов."""

    type = DateTime()  # noqa: A003


class UTCDateTime(TypeDecorator[datetime.datetime]):
    """Класс-декоратор для DateTime для автоматической подстановки tzinfo=UTC."""

    impl = DateTime
    cache_ok = True

    def process_result_value(
        self: 'UTCDateTime',
        value: 'datetime.datetime | None',
        dialect: 'Dialect',  # noqa
    ) -> 'datetime.datetime | None':
        """Метод получения поля.

        Добавляет tzinfo=UTC в дату и время значения.
        """
        if value is not None:
            return value.replace(tzinfo=UTC)
        return None

    def process_bind_param(
        self: 'UTCDateTime',
        value: 'datetime.datetime | None',
        dialect: 'Dialect',  # noqa
    ) -> 'datetime.datetime | None':
        """Метод для присваивания поля.

        Ничего не делает, потому что SqlAlchemy автоматически переводит значение в UTC.
        """
        return value


@compiles(Utcnow, 'postgresql')
def pg_utcnow(type_: Any, compiler: Any, **kwargs: Any):  # noqa
    """Маппинг класса Utcnow на функцию в postgresql."""
    return "TIMEZONE('utc', CURRENT_TIMESTAMP)"
