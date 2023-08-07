from string import Template
from typing import Any

from fastapi import HTTPException, status

from app.core.exceptions.http.base import BaseVerboseHTTPException


class FilterValidationError(HTTPException):
    """Базовая ошибка доступа к ресурсу."""

    _status_code = status.HTTP_422_UNPROCESSABLE_ENTITY

    def __init__(
        self: 'FilterValidationError',
        detail: Any = None,  # noqa: ANN401
        headers: dict[str, str] | None = None,
    ) -> None:
        super().__init__(self._status_code, detail, headers)


class BaseHttpFilterError(BaseVerboseHTTPException):
    """Базовая http-ошибка для фильтров."""

    code = 'incorrect_filter'
    type_ = 'filter_error'
    message = 'Невалидный фильтр.'
    template = Template('Невалидный фильтр: $reason.')


class InvalidFilterFieldError(BaseHttpFilterError):
    """Ошибка поля field у схемы фильтров: у модели нет такого поля."""

    code = 'invalid_filter_field'
