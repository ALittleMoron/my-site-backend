from functools import lru_cache

from app.core.settings.app import AppSettings
from app.core.settings.base import PathSettings
from app.core.settings.db import TORTOISE_ORM, DatabaseSettings  # noqa
from app.core.settings.logger import logger  # noqa


@lru_cache
def get_path_settings() -> PathSettings:
    """Функция достает настройки путей проекта.

    Returns:
        PathSettings: настройки путей.
    """
    return PathSettings()


@lru_cache
def get_application_settings() -> AppSettings:
    """Функция достает настройки приложения для запуска.

    Returns:
        AppSettings: настройки приложения.
    """
    return AppSettings()


@lru_cache
def get_database_settings() -> DatabaseSettings:
    """Функция достает настройки базы данных.

    Returns:
        DatabaseSettings: настройки базы данных.
    """
    return DatabaseSettings()
