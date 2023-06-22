import os

import pytest
from mimesis import Datetime
from mimesis.locales import Locale

from app.utils import env as env_utils

fake_datetimes = Datetime(Locale.EN)
DEFAULT_KEY = 'SOME_TEST_FOO_KEY'


@pytest.mark.parametrize(
    ('key', 'value', 'expected_result'),
    [
        ('MY_SITE_FOO', 'a,b,c,d', ['a', 'b', 'c', 'd']),
        ('AND_OTHER_FOO', 'a,b', ['a', 'b']),
        ('SOME_OTHER_FOO', 'a', ['a']),
        ('LAST_FOO', '', []),
    ],
)
def test_getenv_list(key: str, value: str, expected_result: list[str]) -> None:
    """Проверка работы метода конвертации переменной окружения в список строк.

    Успешный кейс.
    """
    os.environ[key] = value
    assert env_utils.getenv_list(key) == expected_result


@pytest.mark.parametrize(
    ('default', 'expected_result'),
    [
        ('a,b,c,d', ['a', 'b', 'c', 'd']),
        ('a,b', ['a', 'b']),
        ('a', ['a']),
        ('', []),
    ],
)
def test_getenv_list_default(default: str, expected_result: list[str]) -> None:
    """Проверка работы метода конвертации переменной окружения в список строк.

    Кейс c default.
    """
    if DEFAULT_KEY in os.environ:
        del os.environ[DEFAULT_KEY]
    assert env_utils.getenv_list(DEFAULT_KEY, default=default) == expected_result


@pytest.mark.parametrize(
    ('value', 'separator', 'expected_result'),
    [
        ('a,b,c,d', ',', ['a', 'b', 'c', 'd']),
        ('a,b', ',', ['a', 'b']),
        ('a', ',', ['a']),
        ('', ',', []),
        ('a,b,c,d', '.', []),
        ('a,b', '.', []),
        ('a,', '.', []),
        ('', '.', []),
    ],
)
def test_getenv_list_separator(value: str, separator: str, expected_result: list[str]) -> None:
    """Проверка работы метода конвертации переменной окружения в список строк.

    Кейс c separator.
    """
    os.environ[DEFAULT_KEY] = value
    assert env_utils.getenv_list(DEFAULT_KEY, separator=separator) == expected_result


@pytest.mark.parametrize(
    ('key', 'value', 'expected_result'),
    [
        ('MY_SITE_FOO', '124', 124),
        ('AND_OTHER_FOO', '124.0', 124),
        ('SOME_OTHER_FOO', 'abc', None),
        ('LAST_FOO', '', None),
    ],
)
def test_getenv_int(key: str, value: str, expected_result: int | None) -> None:
    """Проверка работы метода конвертации переменной окружения в число."""
    os.environ[key] = value
    assert env_utils.getenv_int(key) == expected_result


@pytest.mark.parametrize(
    ('default', 'expected_result'),
    [(124, 124), (None, None)],
)
def test_getenv_int_default(default: int | None, expected_result: int | None) -> None:
    """Проверка работы метода конвертации переменной окружения в число.

    Кейс c default.
    """
    if DEFAULT_KEY in os.environ:
        del os.environ[DEFAULT_KEY]
    assert env_utils.getenv_int(DEFAULT_KEY, default=default) == expected_result


@pytest.mark.parametrize(
    ('key', 'value', 'expected_result'),
    [
        ('MY_SITE_FOO', '1', True),
        ('AND_OTHER_FOO', 'yes', True),
        ('SOME_OTHER_FOO', 'true', True),
        ('SOME_OTHER_FOO', 'false', False),
        ('LAST_FOO', '', False),
    ],
)
def test_getenv_bool(key: str, value: str, expected_result: bool) -> None:  # noqa: FBT001
    """Проверка работы метода конвертации переменной окружения в булево значение."""
    os.environ[key] = value
    assert env_utils.getenv_bool(key) == expected_result


@pytest.mark.parametrize(
    ('default', 'expected_result'),
    [('', False), ('1', True), ('false', False)],
)
def test_getenv_bool_default(default: str, expected_result: bool) -> None:  # noqa: FBT001
    """Проверка работы метода конвертации переменной окружения в булево значение.

    Кейс с default
    """
    if DEFAULT_KEY in os.environ:
        del os.environ[DEFAULT_KEY]
    assert env_utils.getenv_bool(DEFAULT_KEY, default=default) == expected_result
