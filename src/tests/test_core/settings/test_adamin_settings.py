import os

import pytest
from app.core.settings import admin as admin_settings

TEST_ENV_1 = dict(
    ADMIN_SECRET_KEY='abc',  # noqa: S106
)
TEST_ENV_2 = dict(
    ADMIN_SECRET_KEY='cba',  # noqa: S106
)


@pytest.mark.parametrize('dict_env', [TEST_ENV_1, TEST_ENV_2])
def test_database_settings_contains(dict_env: dict[str, str]) -> None:
    """Проверка значений настроек приложения."""
    os.environ.update(dict_env)
    settings = admin_settings.AdminSettings()

    assert settings.secret_key.get_secret_value() == dict_env.get('ADMIN_SECRET_KEY')
