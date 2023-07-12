"""Модуль настроек логирования.

ВНИМАНИЕ! Не импортируйте объект логирования отсюда! Воспользуйтесь импортом из конфига.
"""
from typing import Any, TypeGuard

import orjson

from .base import LOGS_DIR, STATIC_DIR


def all_dict_str_keys(value: dict[Any, Any]) -> TypeGuard[dict[str, Any]]:
    """TypeGuard, проверяющий ключи в словаре: все ключи - строки."""
    return all(isinstance(key, str) for key in value.keys())  # noqa: SIM118


with (STATIC_DIR / 'default_logger_settings.json').open('r') as reader:
    log_settings_str = reader.read()

try:
    log_settings = orjson.loads(log_settings_str)
    if not isinstance(log_settings, dict):
        msg = (
            'default_logger_settings.json должен содержать объект (словарь), а не список объектов.'
        )
        raise TypeError(msg)  # noqa: TRY301
    if not all_dict_str_keys(log_settings):  # type: ignore
        msg = 'словарь должен содержать ключи только в виде строк.'
        raise TypeError(msg)  # noqa: TRY301
except (orjson.JSONDecodeError, ValueError):
    log_settings = {}


for handler_data in log_settings.get('handlers', {}).values():
    if 'filename' in handler_data:
        filename: str = handler_data['filename']
        handler_data['filename'] = filename.format(path=LOGS_DIR.as_posix())
