"""Модуль настроек логирования.

ВНИМАНИЕ! Не импортируйте объект логирования отсюда! Воспользуйтесь импортом из конфига.
"""
from typing import Any, TypeGuard

import orjson
from pydantic import Field, validator

from .base import LOGS_DIR, STATIC_DIR, ProjectBaseSettings

DictStrAny = dict[str, Any]
FILE_TEMPLATE: str = "{name}.log"


def is_dict_str_keys_only(value: dict[Any, Any]) -> TypeGuard[dict[str, Any]]:
    """TypeGuard, проверяющий ключи в словаре: все ключи - строки."""
    return all(isinstance(key, str) for key in value.keys())  # noqa: SIM118


with (STATIC_DIR / 'default_logger_settings.json').open('r') as reader:
    default_log_settings = reader.read()


class LoggerSettings(ProjectBaseSettings):
    """Класс настроек для базы данных."""

    settings: DictStrAny = Field(
        default=default_log_settings,
        description='все основные настройки логгера',
    )
    has_file_path_template: bool = Field(
        default=True,
        description='в настройках логгера имеется шаблон пути до файла?',
    )
    path_to_log_template_var_name: str = Field(
        default='path',
        description=(
            'название переменной внутри ``filename``, по которой будет форматироваться полный путь '
            'до файла логов'
        ),
    )

    @validator('settings', pre=True)
    @classmethod
    def settings_to_dict(cls: 'type[LoggerSettings]', value: str | dict[str, Any]) -> DictStrAny:
        """Валидатор, конвертирующий настройки логгера из строки в ."""
        not_all_keys_are_str_msg = 'не все ключи в LOGGER_SETTINGS являются строками.'
        if isinstance(value, dict) and is_dict_str_keys_only(value):
            return value
        elif isinstance(value, dict):
            raise ValueError(not_all_keys_are_str_msg)
        try:
            result = orjson.loads(value)
        except orjson.JSONDecodeError as exc:
            msg = (
                f'переменная окружения LOGGER_SETTINGS должна быть json-строкой. '
                f'Переданное значение: {value} (тип: {type(value)})'
            )
            raise ValueError(msg) from exc
        if isinstance(result, dict) and is_dict_str_keys_only(result):  # type: ignore
            return result
        raise ValueError(not_all_keys_are_str_msg)

    def format_settings(self: 'LoggerSettings') -> DictStrAny:
        """Форматирует переданные настройки."""
        if not self.has_file_path_template:
            return self.settings
        for handler_data in self.settings.get('handlers', {}).values():
            if 'filename' in handler_data:
                filename: str = handler_data['filename']
                handler_data['filename'] = filename.format(
                    **{self.path_to_log_template_var_name: LOGS_DIR.as_posix()},
                )
        return self.settings

    class Config:  # type: ignore
        """config class for production settings."""

        env_prefix = "LOGGER_"
