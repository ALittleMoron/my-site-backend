"""Модуль настроек приложения FastAPI."""
import enum
import pathlib
from typing import Any, TypedDict

from fastapi.openapi.models import Contact, License, Server
from pydantic import AnyHttpUrl, Field

from app.core.settings.base import APP_DIR, ProjectBaseSettings


class ThemeEnum(str, enum.Enum):
    """Enum тем Swagger UI."""

    AGATE = "agate"
    ARTA = "arta"
    MONOKAI = "monokai"
    NORD = "nord"
    OBSIDIAN = "obsidian"
    TOMORROW_NIGHT = "tomorrow-night"


class FastAPIKwargs(TypedDict):
    """Типизированный словарь kwargs параметров для FastAPI.."""

    debug: bool
    docs_url: str
    openapi_prefix: str
    openapi_url: str
    redoc_url: str
    swagger_ui_oauth2_redirect_url: str | None
    swagger_ui_parameters: dict[str, str | Any] | None
    swagger_ui_init_oauth: dict[str, str | Any] | None
    title: str
    version: str
    root_path: str
    root_path_in_servers: bool
    term_of_service: str | None
    contact: dict[str, str | Any] | None
    license_info: dict[str, str | Any] | None
    servers: list[dict[str, str | Any]] | None


class FastAPISwaggerUIParameters(TypedDict):
    """Типизированный словарь параметров UI Swagger'а для FastAPI."""


class AppSettings(ProjectBaseSettings):
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
    swagger_ui_oauth2_redirect_url: str | None = Field(
        default='/docs/oauth2-redirect',
        description='Ссылка для переадресации в oauth2 авторизации в документации.',
    )
    swagger_ui_syntax_highlight: bool = Field(
        default=True,
        description='Подсвечивать ли синтаксис JSON в Swagger UI?',
    )
    swagger_ui_deep_linking: bool = Field(
        default=True,
        description="Поддержка deep link'ов в Swagger UI.",
    )
    swagger_ui_dom_id: str = Field(
        default='#swagger-ui',
        description='id DOM в Swagger UI.',
    )
    swagger_ui_layout: str = Field(
        default='BaseLayout',
        description='Имя компонента Swagger UI (доступно с плагинами).',
    )
    swagger_ui_show_extensions: bool = Field(
        default=True,
        description='Показывать расширения (схемы, X- параметры и т.д.).',
    )
    swagger_ui_show_common_extensions: bool = Field(
        default=True,
        description='Показывать расширения (pattern, maxLength, minLength, maximum, minimum).',
    )
    swagger_ui_syntax_highlight_theme: ThemeEnum | None = Field(
        default=ThemeEnum.OBSIDIAN,
        description='Тема подсветки синтаксиса в Swagger UI.',
    )
    # TODO: swagger_ui_init_oauth - не поле, но всякие разные поля, которые будут конвертироваться
    # https://github.com/swagger-api/swagger-ui/blob/master/docs/usage/oauth2.md
    title: str = Field(
        default='FastAPI example application',
        description='Заголовок документации',
    )
    version: str = Field(
        default='0.0.0',
        description='Версия API',
    )
    root_path: str = Field(
        default='',
        description='Путь до корня пути API',
    )
    root_path_in_servers: bool = Field(
        default=True,
        description='Включать ли root_path для серверов (servers)?',
    )
    term_of_service: AnyHttpUrl | None = Field(
        default=None,
        description='Пользовательское соглашение',
    )
    contact: Contact | None = Field(
        default=None,
        description='Данные моих контактов',
    )
    license: License | None = Field(  # noqa: A003
        default=None,
        description='Данные лицензии приложения',
    )
    servers: list[Server] | None = Field(
        default=None,
        description='Сервера приложения',
    )

    path_to_description: pathlib.Path = APP_DIR / 'openapi_description.md'

    @property
    def fastapi_kwargs(self: 'AppSettings') -> FastAPIKwargs:
        """Свойство, возвращающее настройки для FastAPI в виде словаря.

        Returns
        -------
        FastAPIKwargs
            словарь настроек.
        """
        return {
            'debug': self.debug,
            'docs_url': self.docs_url,
            'openapi_prefix': self.openapi_prefix,
            'openapi_url': self.openapi_url,
            'redoc_url': self.redoc_url,
            'swagger_ui_oauth2_redirect_url': self.swagger_ui_oauth2_redirect_url,
            'swagger_ui_init_oauth': {},
            'swagger_ui_parameters': {
                'dom_id': self.swagger_ui_dom_id,
                'layout': self.swagger_ui_layout,
                'deepLinking': self.swagger_ui_deep_linking,
                'showExtensions': self.swagger_ui_show_extensions,
                'showCommonExtensions': self.swagger_ui_show_common_extensions,
                'syntaxHighlight': self.swagger_ui_syntax_highlight,
                'syntaxHighlight.theme': self.swagger_ui_syntax_highlight_theme,
            },
            'title': self.title,
            'version': self.version,
            'root_path': self.root_path,
            'root_path_in_servers': self.root_path_in_servers,
            'term_of_service': self.term_of_service,
            'contact': self.contact.dict() if self.contact else None,
            'license_info': self.license.dict() if self.license else None,
            'servers': [server.dict() for server in self.servers] if self.servers else None,
        }

    class Config:  # type: ignore
        """Класс-конфиг для приложения."""

        env_prefix = 'APP_'
