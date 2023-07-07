import os

import pytest

from app.core.settings import db as db_settings

TEST_ENV_1 = dict(
    DB_USER='test_user',
    DB_PASSWORD='1234',  # noqa: S106
    DB_NAME='test_db',
    DB_HOST='localhost',
    DB_PORT='5432',
    DB_ENGINE='asyncpg',
    DB_TYPE_='postgresql',
)
TEST_ENV_2 = dict(
    DB_USER='changed_user',
    DB_PASSWORD='4321',  # noqa: S106
    DB_NAME='changed_db',
    DB_HOST='not_local_host',
    DB_PORT='7654',
    DB_ENGINE='any_of_other',
    DB_TYPE_='sqlite',
)


@pytest.mark.parametrize('dict_env', [TEST_ENV_1, TEST_ENV_2])
def test_database_settings_contains(dict_env: dict[str, str]) -> None:
    """Проверка значений настроек приложения."""
    os.environ.update(dict_env)
    settings = db_settings.DatabaseSettings()

    assert settings.user == dict_env.get('DB_USER')
    assert settings.password == dict_env.get('DB_PASSWORD')
    assert settings.name == dict_env.get('DB_NAME')
    assert settings.host == dict_env.get('DB_HOST')
    assert settings.port == int(dict_env.get('DB_PORT', ''))
    assert settings.engine == dict_env.get('DB_ENGINE')
    assert settings.type_ == dict_env.get('DB_TYPE_')


@pytest.mark.parametrize('dict_env', [TEST_ENV_1, TEST_ENV_2])
def test_database_settings_db_url(dict_env: dict[str, str]) -> None:
    """Проверка значений свойства fastapi_kwargs."""
    os.environ.update(dict_env)
    settings = db_settings.DatabaseSettings()
    db_url = settings.db_url
    test_db_url = db_settings.DB_URL_TEMPLATE.format(
        type=settings.type_,
        engine=settings.engine,
        user=settings.user,
        password=settings.password,
        host=settings.host,
        port=settings.port,
        name=settings.name,
    )
    assert db_url == test_db_url
