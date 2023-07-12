"""Модуль настроек базы данных проекта."""
from pydantic import Field, IPvAnyAddress
from pydantic_settings import SettingsConfigDict

from .base import ProjectBaseSettings

POSTGRESQL_URL_TEMPLATE = "{type}://{user}:{password}@{host}:{port}/{name}"
DB_URL_TEMPLATE = "{type}+{engine}://{user}:{password}@{host}:{port}/{name}"


class DatabaseSettings(ProjectBaseSettings):
    """Класс настроек для базы данных."""

    model_config = SettingsConfigDict(env_prefix='DB_')

    user: str = Field(default='test_user', description='Пользователь базы данных')
    password: str = Field(default='1234', description='Пароль пользователя')
    name: str = Field(default='test_db', description='Имя базы данных')
    host: IPvAnyAddress | str = Field(default='localhost', description='Хост базы данных')
    port: int = Field(default=5432, description='Порт базы данных')
    engine: str = Field(default='asyncpg', description='движок (драйвер) подключения к базе данных')
    type_: str = Field(default='postgresql', description='база данных')

    @property
    def asyncpg_postgresql_url(self: 'DatabaseSettings') -> str:
        """Свойство, возвращающее ссылку на ."""
        return POSTGRESQL_URL_TEMPLATE.format(
            type=self.type_,
            user=self.user,
            password=self.password,
            host=self.host,
            port=self.port,
            name='postgres',
        )

    @property
    def db_url(self: 'DatabaseSettings') -> str:
        """Свойство, возвращающее ссылку на базу данных.

        Returns
        -------
            str: ссылка на базу данных.
        """
        return DB_URL_TEMPLATE.format(
            type=self.type_,
            engine=self.engine,
            user=self.user,
            password=self.password,
            host=self.host,
            port=self.port,
            name=self.name,
        )

    @property
    def test_db_url(self: 'DatabaseSettings') -> str:
        """Свойство, возвращающее ссылку на тестовую базу данных.

        Returns
        -------
            str: ссылка на базу данных.
        """
        return DB_URL_TEMPLATE.format(
            type=self.type_,
            engine=self.engine,
            user=self.user,
            password=self.password,
            host=self.host,
            port=self.port,
            name='pytest_db',
        )
