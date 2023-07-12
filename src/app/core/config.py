"""Модуль конфига проекта.

Содержит кэшированные функции, возвращающие инициализированные экземпляры `pydantic.BaseSettings`,
а также другие объекты, подходящие под критерии данного модуля (экземпляр класса для логирования,
например).
"""
import logging
import logging.config
from functools import lru_cache

from app.core.settings.app import AppSettings
from app.core.settings.base import PathSettings
from app.core.settings.db import DatabaseSettings
from app.core.settings.logger import log_settings


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


@lru_cache
def get_logger(name: str) -> logging.Logger:
    """Возвращает логгер по его имени.

    Parameters
    ----------
    name : str
        название логгера

    Returns
    -------
    logging.Logger
        экземпляр логгера.
    """
    logging.config.dictConfig(log_settings)
    return logging.getLogger(name)
