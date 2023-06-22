"""Модуль базовых enum'ов моделей проекта."""
import enum

from dateutil.relativedelta import relativedelta


class StrTimedeltaEnum(str, enum.Enum):
    """Базовый Enum для хранения дельты времени вместе с произвольной строкой.

    Пример объявления:
    ```
        class ReminderRepeatTypeEnum(StrTimedeltaEnum):
            '''Enum типов повторов напоминаний.'''

            NEVER = 'never'
            DAILY = ('daily', relativedelta(days=1))
            WEEKLY = ('weekly', relativedelta(weeks=1))
            MONTHLY = ('monthly', relativedelta(months=1))
            EVERY_THREE_MONTHS = ('every3Months', relativedelta(months=3))
            EVERY_SIX_MONTHS = ('every6Months', relativedelta(months=6))
            YEARLY = ('yearly', relativedelta(years=1))

    ```
    В данном случае мы имеем класс с установленными дельтами времени. Примеры использования:

    >>> ReminderRepeatTypeEnum.WEEKLY.name
    'WEEKLY'

    >>> ReminderRepeatTypeEnum.WEEKLY.value
    'weekly'

    >>> ReminderRepeatTypeEnum.WEEKLY.timedelta
    relativedelta(days=+7)

    """

    timedelta: relativedelta

    def __new__(
        cls: 'type[StrTimedeltaEnum]',
        title: str,
        timedelta: relativedelta | None = None,
    ) -> 'StrTimedeltaEnum':
        """Переопределенный метод __new__ для реализации хранения дельты времени.

        Parameters
        ----------
        title
            первый аргумент строкового enum'а по умолчанию.
        timedelta
            экземпляр класса relativedelta.

        Returns
        -------
        StrTimedeltaEnum
            экземпляр класса StrTimedeltaEnum.
        """
        obj = str.__new__(cls, title)
        obj._value_ = title
        if timedelta is None:
            timedelta = relativedelta()
        obj.timedelta = timedelta
        return obj
