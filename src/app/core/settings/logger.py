"""Модуль настроек логирования.

ВНИМАНИЕ! Не импортируйте объект логирования отсюда! Воспользуйтесь импортом из конфига.
"""
from enum import Enum
from typing import Literal

from loguru import logger

from .base import PROJECT_ROOT_DIR

LOGGER_FOLDER: Literal["logs"] = "logs"
LOGGER_FILE_TEMPLATE = "{log_level}_{unique}.log"
LOGGER_FILE_PATH_TEMPLATES: dict[int, str] = {}

if not (_dir := (PROJECT_ROOT_DIR / LOGGER_FOLDER)).exists():
    _dir.mkdir(exist_ok=True)


class LogLevels(int, Enum):
    """Log levels from logging module as enum class."""

    DEBUG = 10
    INFO = 20
    WARNING = 30
    ERROR = 40


for log_dir_element in (PROJECT_ROOT_DIR / LOGGER_FOLDER).iterdir():
    if log_dir_element.is_file() and log_dir_element.stat().st_size == 0:
        log_dir_element.unlink(missing_ok=True)


for log_level in LogLevels:
    LOGGER_FILE_PATH_TEMPLATES.update(
        {
            log_level.value: (
                template := (
                    PROJECT_ROOT_DIR
                    / LOGGER_FOLDER
                    / LOGGER_FILE_TEMPLATE.format(
                        log_level=log_level.name.upper(),
                        unique="{time}",
                    )
                )
                .absolute()
                .as_posix()
            ),
        },
    )
    logger.add(template, level=log_level.name, rotation="100 MB")
