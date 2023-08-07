"""Модуль кастомных функций-операторов."""
from typing import TYPE_CHECKING, Any, Literal, TypeVar, overload

from sqlalchemy import and_, false

if TYPE_CHECKING:
    from collections.abc import Sequence

    from sqlalchemy.sql.elements import ColumnElement

    T = TypeVar('T')


def do_nothing(*args: Any, **kwargs: Any) -> None:  # noqa: ANN401
    """Ничего не делает, ничего не возвращает."""
    return None


def return_value(value: 'T') -> 'T':
    """Ничего не делает, и возвращает переданное значение."""
    return value


@overload
def between(
    a: Any,  # noqa: ANN401
    b: 'tuple[Any, Any]',
    *,
    sqlalchemy_mode: Literal[False] = False,
) -> bool:
    ...


@overload
def between(
    a: Any,  # noqa: ANN401
    b: 'tuple[Any, Any]',
    *,
    sqlalchemy_mode: Literal[True] = True,
) -> 'ColumnElement[bool]':
    ...


def between(
    a: Any,  # noqa: ANN401
    b: tuple[Any, Any],
    *,
    sqlalchemy_mode: bool = False,
) -> 'bool | ColumnElement[bool]':
    """Оператор для проверки вхождения a в диапазон b.

    b - список, состоящий из 2 элементов (левая и правая точка вхождения). Проверка делается с
    включением крайних точек (>= и <=).
    """
    if len(b) != 2:
        if sqlalchemy_mode:
            return false()
        return False
    if sqlalchemy_mode:
        return and_(a >= b[0], a <= b[1])
    return b[0] <= a <= b[1]


@overload
def contains(
    a: Any,  # noqa: ANN401
    b: 'Sequence[Any]',
    *,
    sqlalchemy_mode: Literal[False] = False,
) -> bool:
    ...


@overload
def contains(
    a: Any,  # noqa: ANN401
    b: 'Sequence[Any]',
    *,
    sqlalchemy_mode: Literal[True] = True,
) -> 'ColumnElement[bool]':
    ...


def contains(
    a: Any,  # noqa: ANN401
    b: 'Sequence[Any]',
    *,
    sqlalchemy_mode: bool = False,
) -> 'bool | ColumnElement[bool]':
    """Оператор для проверки вхождения a в неограниченную последовательность b."""
    if sqlalchemy_mode:
        return a.in_(b)
    return a in b
