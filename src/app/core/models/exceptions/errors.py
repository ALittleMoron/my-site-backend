"""Модуль исключения моделей проекта."""
from . import content


class ModelAttributeError(AttributeError):
    """Ошибка атрибута модели."""

    template: str | None = None  # TODO: переделать под Template

    def __init__(self: 'ModelAttributeError', **kwargs: object) -> None:  # noqa: D107
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
