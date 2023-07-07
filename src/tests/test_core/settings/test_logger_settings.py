import os
from itertools import zip_longest
from typing import Any

import orjson
import pytest

from app.core.settings import logger as logger_settings
from app.core.settings.base import LOGS_DIR, TESTS_DIR

with (TESTS_DIR / 'files' / 'default_logger_settings.json').open('r') as reader:
    logger_settings_1 = reader.read()
with (TESTS_DIR / 'files' / 'override_logger_settings.json').open('r') as reader:
    logger_settings_2 = reader.read()
TEST_ENV_1 = dict(
    LOGGER_PATH_TO_LOGS='/vars/logs',
    LOGGER_SETTINGS=logger_settings_1,
    LOGGER_HAS_FILE_PATH_TEMPLATE='true',
    LOGGER_PATH_TO_LOG_TEMPLATE_VAR_NAME='path',
)
TEST_ENV_2 = dict(
    LOGGER_PATH_TO_LOGS='/temp/',
    LOGGER_SETTINGS=logger_settings_2,
    LOGGER_HAS_FILE_PATH_TEMPLATE='true',
    LOGGER_PATH_TO_LOG_TEMPLATE_VAR_NAME='path',
)


@pytest.mark.parametrize('dict_env', [TEST_ENV_1, TEST_ENV_2])
def test_database_settings_contains(dict_env: dict[str, str]) -> None:
    """Проверка значений настроек приложения."""
    os.environ.update(dict_env)
    settings = logger_settings.LoggerSettings()

    assert settings.settings == orjson.loads(dict_env.get('LOGGER_SETTINGS', ''))
    assert settings.has_file_path_template == (
        dict_env.get('LOGGER_HAS_FILE_PATH_TEMPLATE') == 'true'
    )
    assert settings.path_to_log_template_var_name == dict_env.get(
        'LOGGER_PATH_TO_LOG_TEMPLATE_VAR_NAME',
    )


@pytest.mark.parametrize('dict_env', [TEST_ENV_1, TEST_ENV_2])
def test_logger_settings_format_settings(dict_env: dict[str, str]) -> None:
    """Проверка значений свойства fastapi_kwargs."""
    os.environ.update(dict_env)
    settings = logger_settings.LoggerSettings()

    not_formatted_settings: dict[str, Any] = orjson.loads(dict_env['LOGGER_SETTINGS'])
    formatted_settings = settings.format_settings()
    for formatted_handler, not_formatted_handler in zip_longest(
        formatted_settings.get('handlers', {}).values(),
        not_formatted_settings.get('handlers', {}).values(),
        fillvalue=None,
    ):
        if 'filename' in formatted_handler and 'filename' in not_formatted_handler:  # type: ignore
            assert formatted_handler['filename'] == not_formatted_handler[  # type: ignore
                'filename'
            ].format(  # type: ignore
                **{settings.path_to_log_template_var_name: LOGS_DIR.as_posix()},
            )
        elif (
            'filename' in formatted_handler  # type: ignore
            and 'filename' not in not_formatted_handler  # type: ignore
        ) or (
            'filename' not in formatted_handler  # type: ignore
            and 'filename' in not_formatted_handler  # type: ignore
        ):
            pytest.fail('filename должен быть в обеих проверяемых сущностях, либо ни в одной.')
