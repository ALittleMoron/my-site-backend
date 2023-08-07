import enum
import operator as builtin_operators
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel

from app.utils import operators as custom_operators

if TYPE_CHECKING:
    from collections.abc import Callable

    from sqlalchemy.sql.elements import ClauseElement


class FilterOperatorEnum(str, enum.Enum):
    """Enum фильтрующих операторов.

    Хранит дополнительную информацию: функцию оператора (по умолчанию используется оператор,
    который не делает ничего).
    """

    func: 'Callable[[Any, Any], bool | ClauseElement]'

    EQUALS = '=', builtin_operators.eq
    GREATER_THAN = '>', builtin_operators.gt
    LESS_THAN = '<', builtin_operators.lt
    GREATER_THAN_OR_EQUAL = '>=', builtin_operators.ge
    LESS_THAN_OR_EQUAL = '<=', builtin_operators.le
    BETWEEN = 'between', custom_operators.between
    CONTAINS = 'contains', custom_operators.contains

    def __new__(  # noqa: D102
        cls: type['FilterOperatorEnum'],
        title: str,
        func: 'Callable[[Any, Any], bool | ClauseElement]',
    ) -> 'FilterOperatorEnum':
        obj = str.__new__(cls, title)
        obj._value_ = title
        obj.func = func
        return obj


class FilterSchema(BaseModel):
    """Схема фильтров."""

    field: str
    value: Any
    operator: FilterOperatorEnum
