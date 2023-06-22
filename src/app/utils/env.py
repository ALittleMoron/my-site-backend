"""Модуль утилит для работы с переменными окружения.

Базово все переменные окружения отлавливаются в классах настроек `pydantic.BaseSettings`, но есть
сценарии, когда нужно вручную забрать какую-то переменную окружения. Для этого нужны функции
этого модуля.
"""
import os


def getenv_list(key: str, default: str = '', separator: str = ',') -> list[str]:
    """Функция, преобразующая переменную окружения в список.

    Parameters
    ----------
    key
        имя переменной, которую нужно достать из окружения.
    default
        значение по умолчанию. Default to ''.
    separator
        разделитель для парсинга значений списка. Defaults to ','.

    Returns
    -------
    list of str
        итоговый список, полученный из переменных окружения.
    """
    value = os.getenv(key, default)
    if separator not in value and not value.isalnum():
        return []
    result_list = [x.strip() for x in value.strip().split(separator)]
    return list(filter(lambda x: x, result_list))


def getenv_bool(key: str, default: str = '') -> bool:  # noqa: FNE005
    """Функция, преобразующая переменную окружения в булево значение.

    Parameters
    ----------
    key
        имя переменной, которую нужно достать из окружения.
    default
        значение по умолчанию. Default to ''.

    Returns
    -------
    bool
        итоговое булево значение, полученное из переменных окружения.
    """
    return os.getenv(key, default).lower() in ('1', 'true', 'yes')


def getenv_int(key: str, default: int | None = None) -> int | None:
    """Функция, преобразующая переменную окружения в целочисленное значение.

    Parameters
    ----------
    key
        имя переменной, которую нужно достать из окружения.
    default
        значение по умолчанию. Default to None.

    Returns
    -------
    int, optional
        итоговое число, полученное из переменных окружения.
    """
    value = os.getenv(key, '')
    try:
        return int(float(value))
    except ValueError:
        return default
