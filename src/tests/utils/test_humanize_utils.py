import pytest

from app.utils import humanize as humanize_utils

DEFAULT_SIZE = 1024


@pytest.mark.parametrize(
    ('size', 'suffix', 'expected_result'),
    [
        (1023, 'b', '1023b'),
        (1024, 'b', '1Kb'),
        (1024**2, 'b', '1Mb'),
        (1024**3, 'b', '1Gb'),
        (1024**4, 'b', '1Tb'),
        (1024**5, 'b', '1Pb'),
        (1024**6, 'b', '1Eb'),
        (1024**7, 'b', '1Zb'),
        (1024**8, 'b', '1Yb'),
    ],
)
def test_sizeof_fmt(size: int | float, suffix: str, expected_result: str) -> None:
    """Проверка работы функции конвертации числа байт в человекочитаемый вид."""
    assert humanize_utils.sizeof_fmt(size, suffix=suffix) == expected_result


@pytest.mark.parametrize(
    ('suffix', 'expected_result'),
    [
        ('b', '1Kb'),
        ('ib', '1Kib'),
        ('abc', '1Kabc'),
    ],
)
def test_sizeof_fmt_suffix(suffix: str, expected_result: str) -> None:
    """Проверка работы функции конвертации числа байт в человекочитаемый вид.

    Кейс с suffix.
    """
    assert humanize_utils.sizeof_fmt(DEFAULT_SIZE, suffix=suffix) == expected_result


@pytest.mark.parametrize(
    ('size', 'suffix', 'expected_result'),
    [
        (1023, 'b', '1023.0b'),
        (1024, 'b', '1.0Kb'),
        (1024**2, 'b', '1.0Mb'),
        (1024**3, 'b', '1.0Gb'),
        (1024**4, 'b', '1.0Tb'),
        (1024**5, 'b', '1.0Pb'),
        (1024**6, 'b', '1.0Eb'),
        (1024**7, 'b', '1.0Zb'),
        (1024**8, 'b', '1.0Yb'),
    ],
)
def test_sizeof_fmt_with_force_float(size: int | float, suffix: str, expected_result: str) -> None:
    """Проверка работы функции конвертации числа байт в человекочитаемый вид."""
    assert humanize_utils.sizeof_fmt(size, suffix=suffix, force_float=True) == expected_result
