"""Модуль утилит для админ-панели."""
import enum
from typing import TYPE_CHECKING, TypeVar

from app.core.config import get_logger

if TYPE_CHECKING:
    from collections.abc import Iterable

    from sqladmin import Admin, BaseView

    from app.core.models.tables.base import Base


logger = get_logger('app')
T = TypeVar('T')


def admin_bulk_add_views(admin: 'Admin', views: 'Iterable[type[BaseView]]') -> None:
    """Функция для добавления нескольких страниц админ-панели (views) в цикле."""
    for view in views:
        admin.add_view(view)


def enum_field_verbose(model_instance: 'Base', attribute_name: str) -> str:
    """Заменяет enum.name на enum.value в выводе поля сущности."""
    incorrect_value = '<Incorrect field>'
    field_value = getattr(model_instance, attribute_name, incorrect_value)
    if isinstance(field_value, enum.Enum):
        field_value = field_value.value
    else:
        cls_name = model_instance.__class__.__name__
        logger.warning(
            'ENUM-FIELD-VERBOSE W: поле "%s" нет в модели %s или оно не является перечислением.',
            attribute_name,
            cls_name,
        )
    return str(field_value)
