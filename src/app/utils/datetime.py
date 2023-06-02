"""Модуль утилит для работы с датой и временем."""

import datetime
import zoneinfo


def get_utc_now() -> datetime.datetime:
    """возвращает текущее UTC время.

    Returns:
        datetime: текущая дата и время во временной зоне UTC.
    """
    return datetime.datetime.now(zoneinfo.ZoneInfo('UTC'))
