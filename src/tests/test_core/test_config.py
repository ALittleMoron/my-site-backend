from typing import TYPE_CHECKING

import pytest
from app.core import config

if TYPE_CHECKING:
    from collections.abc import Callable

    from pydantic_settings import BaseSettings


@pytest.mark.parametrize(
    'function_to_call',
    [
        config.get_application_settings,
        config.get_database_settings,
        config.get_path_settings,
    ],
)
def test_config_lru(function_to_call: 'Callable[[], BaseSettings]') -> None:
    """Проверка работы lru_cache."""
    assert function_to_call() is function_to_call()


@pytest.mark.parametrize(
    ('function_to_call', 'settings_class'),
    [
        (config.get_application_settings, config.AppSettings),
        (config.get_database_settings, config.DatabaseSettings),
        (config.get_path_settings, config.PathSettings),
    ],
)
def test_config_contains(
    function_to_call: 'Callable[[], BaseSettings]',
    settings_class: 'type[BaseSettings]',
) -> None:
    """Проверка содержимого функций конфигураций."""
    assert function_to_call().model_dump() == settings_class().model_dump()


def test_config_get_logger() -> None:
    """Проверка возврата логгера."""
    assert config.get_logger('app') is config.get_logger('app')
