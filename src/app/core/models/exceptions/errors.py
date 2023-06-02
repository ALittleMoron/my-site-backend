"""Модуль исключения моделей проекта."""
from typing import Any, Optional

from . import content


class ModelAttributeError(AttributeError):
    """Ошибка атрибута модели."""

    template: Optional[str] = None  # TODO: переделать под Template

    def __init__(self, **kwargs: Any) -> None:  # noqa: D107
        if not self.template:
            raise NotImplementedError(content.TEMPLATE_NOT_IMPLEMENTED)
        message = self.template.format(**kwargs)
        super().__init__(message)


class InvalidModelAttributeNameError(ModelAttributeError):
    """Ошибка отсутствия атрибута модели."""

    template = 'Модель {model_name} не содержит атрибут с именем "{attr_name}".'


class NotSetModelAttributeError(ModelAttributeError):
    """Ошибка не установленного значения атрибута модели."""

    template = 'Установите значение атрибута "{attr_name}" в модели {model_name}.'
