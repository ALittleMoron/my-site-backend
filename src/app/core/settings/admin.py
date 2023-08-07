"""Модуль настроек админ-панели проекта."""
from pydantic import Field, SecretStr
from pydantic_settings import SettingsConfigDict

from .base import ProjectBaseSettings


class AdminSettings(ProjectBaseSettings):
    """Класс настроек для админ-панели."""

    model_config = SettingsConfigDict(env_prefix='ADMIN_')

    secret_key: SecretStr = Field(
        default='some_secret_key',
        description='Секретный ключ для работы авторизации.',
    )
