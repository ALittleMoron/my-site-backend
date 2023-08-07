"""Модуль настроек системы авторизации/регистрации на проекте."""
from pydantic import Field, SecretStr
from pydantic_settings import SettingsConfigDict

from .base import ProjectBaseSettings


class AuthSettings(ProjectBaseSettings):
    """Класс настроек системы авторизации/регистрации."""

    model_config = SettingsConfigDict(env_prefix='ADMIN_')

    access_secret_key: SecretStr = Field(
        default='some_access_secret_key',
        description='Секретный ключ для работы JWT-токенами (access).',
    )
    access_expire_time: int = Field(
        default=60 * 10,  # 10 минут
        description='Время жизни access-токена.',
    )
    refresh_secret_key: SecretStr = Field(
        default='some_refresh_secret_key',
        description='Секретный ключ для работы JWT-токенами (refresh).',
    )
    refresh_expire_time: int = Field(
        default=60 * 60 * 24 * 7,  # 7 дней
        description='Время жизни refresh-токена.',
    )
    hasher_schema: list[str] = Field(
        default=['bcrypt'],
        description='Схемы для хеширования.',
    )
    hasher_algorithm: str = Field(
        default='HS256',
        description='Алгоритмы для хеширования.',
    )
