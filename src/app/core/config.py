"""Модуль конфига проекта.

Содержит кэшированные функции, возвращающие инициализированные экземпляры `pydantic.BaseSettings`,
а также другие объекты, подходящие под критерии данного модуля (экземпляр класса для логирования,
например).
"""
from functools import lru_cache

from app.core.settings.app import AppSettings
from app.core.settings.base import PathSettings
from app.core.settings.db import DatabaseSettings
from app.core.settings.logger import logger  # noqa  # type: ignore


@lru_cache
def get_path_settings() -> PathSettings:
    """Функция достает настройки путей проекта.

    Returns
    -------
    PathSettings
        настройки путей.
    """
    return PathSettings()


@lru_cache
def get_application_settings() -> AppSettings:
    """Функция достает настройки приложения для запуска.

    Returns
    -------
    AppSettings
        настройки приложения.
    """
    return AppSettings()


@lru_cache
def get_database_settings() -> DatabaseSettings:
    """Функция достает настройки базы данных.

    Returns
    -------
    DatabaseSettings
        настройки базы данных.
    """
    return DatabaseSettings()
