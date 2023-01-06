from pydantic import BaseSettings, Field, IPvAnyAddress

from .base import BaseConfig

DB_URL_TEMPLATE = "{engine}://{user}:{password}@{host}:{port}/{name}"


class DatabaseSettings(BaseSettings):
    """Класс Setting для базы данных."""

    user: str = Field(default='test_user', description='Пользователь базы данных')
    password: str = Field(default='1234', description='Пароль пользователя')
    name: str = Field(default='test_db', description='Имя базы данных')
    host: IPvAnyAddress | str = Field(default='localhost', description='Хост базы данных')
    port: int = Field(default=5432, description='Порт базы данных')
    engine: str = Field(default='asyncpg', description='движок (драйвер) подключения к базе данных')

    @property
    def db_url(self) -> str:
        """Свойство db_url, возвращающее ссылку на базу данных.

        Returns:
            str: ссылка на базу данных.
        """
        return DB_URL_TEMPLATE.format(
            engine=self.engine,
            user=self.user,
            password=self.password,
            host=self.host,
            port=self.port,
            name=self.name,
        )

    class Config(BaseConfig):  # type: ignore
        """config class for production settings."""

        env_prefix = "DB_"


database_settings = DatabaseSettings()

TORTOISE_ORM = {
    'connections': {'default': database_settings.db_url},
    'apps': {
        'models': {
            'models': ['app.core.models.tables', 'aerich.models'],
            'default_connection': 'default',
        },
    },
    'timezone': 'UTC',
    'use_tz': True,
}
