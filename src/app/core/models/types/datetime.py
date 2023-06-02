"""Модуль типов данных моделей проекта, связанный с датами и временем."""
import zoneinfo
from typing import TYPE_CHECKING, Any, Optional

from sqlalchemy import DateTime, TypeDecorator
from sqlalchemy.ext.compiler import compiles  # type: ignore
from sqlalchemy.sql import expression

if TYPE_CHECKING:
    import datetime

    from sqlalchemy import Dialect


UTC = zoneinfo.ZoneInfo('UTC')


class Utcnow(expression.FunctionElement):  # type: ignore
    """Функция-конструкция для sql запросов."""

    type = DateTime()  # noqa: VNE003


class UTCDateTime(TypeDecorator):  # type: ignore
    """Класс-декоратор для DateTime для автоматической подстановки tzinfo=UTC."""

    impl = DateTime
    cache_ok = True

    def process_result_value(self, value: Optional['datetime.datetime'], dialect: 'Dialect'):
        """Метод получения поля.

        Добавляет tzinfo=UTC в дату и время значения.
        """  # noqa
        if value is not None:
            return value.replace(tzinfo=UTC)
        return None

    def process_bind_param(self, value: Optional['datetime.datetime'], dialect: 'Dialect'):
        """Метод для присваивания поля.

        Ничего не делает, потому что SqlAlchemy автоматически переводит значение в UTC.
        """  # noqa
        return value


@compiles(Utcnow, 'postgresql')
def pg_utcnow(_: Any, __: Any, **___: Any):
    """Маппинг класса Utcnow на функцию в postgresql."""
    return "TIMEZONE('utc', CURRENT_TIMESTAMP)"  # noqa
