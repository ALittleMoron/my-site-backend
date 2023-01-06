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

    TRACE = 5
    DEBUG = 10
    INFO = 20
    SUCCESS = 25
    WARNING = 30
    ERROR = 40
    CRITICAL = 50


for log_level in LogLevels:
    LOGGER_FILE_PATH_TEMPLATES.update(
        {
            log_level.value: (
                template := (
                    PROJECT_ROOT_DIR
                    / LOGGER_FOLDER
                    / log_level.name.lower()
                    / LOGGER_FILE_TEMPLATE.format(
                        log_level=log_level,
                        unique="{time}",
                    )
                )
                .absolute()
                .as_posix()
            ),
        },
    )
    logger.add(template, level=log_level.name, rotation="100 MB")
