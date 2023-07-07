import pytest

from app.utils import strings as string_utils


@pytest.mark.parametrize(
    ('value', 'expected_result'),
    [
        ('{}', True),
        ('{some_var}', True),
        ('{}}', False),
        ('{{}}', False),
        ('{{{{{{}}}{{}{}}', False),
        ('}}{{', False),
        ('}{', False),
    ],
)
def test_has_format_brackets(value: str, expected_result: bool) -> None:  # noqa: FBT001
    """Проверка работы функции конвертации числа байт в человекочитаемый вид."""
    assert string_utils.has_format_brackets(value) == expected_result
