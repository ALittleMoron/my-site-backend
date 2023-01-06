from typing import Any

from pydantic import BaseSettings, Field

from app.core.settings.base import BaseConfig


class AppSettings(BaseSettings):
    """Класс настроек для экземпляра класса FastAPI."""

    debug: bool = Field(
        default=False,
        description='Debug-режим для подробных ответов эндпоинтов',
    )
    docs_url: str = Field(
        default='/docs',
        description='Относительный путь к документации (swagger)',
    )
    openapi_prefix: str = Field(
        default='',
        description='Префикс относительного пути к openapi.json файлу',
    )
    openapi_url: str = Field(
        default='/openapi.json',
        description='Относительный путь к openapi.json файлу',
    )
    redoc_url: str = Field(
        default='/redoc',
        description='Относительный путь к документации (redoc)',
    )
    title: str = Field(
        default='FastAPI example application',
        description='Заголовок документации',
    )
    version: str = Field(
        default='0.0.0',
        description='Версия API',
    )

    @property
    def fastapi_kwargs(self) -> dict[str, Any]:
        """Свойство, возвращающее настройки для FastAPI в виде словаря.

        Returns:
            dict[str, Any]: словарь настроек.
        """
        return {
            'debug': self.debug,
            'docs_url': self.docs_url,
            'openapi_prefix': self.openapi_prefix,
            'openapi_url': self.openapi_url,
            'redoc_url': self.redoc_url,
            'title': self.title,
            'version': self.version,
        }

    class Config(BaseConfig):  # type: ignore
        """Класс-конфиг для приложения."""

        env_prefix = 'APP_'
