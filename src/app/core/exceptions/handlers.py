"""Модуль обработчиков исключений для FastAPI."""
from typing import TYPE_CHECKING

from fastapi.responses import JSONResponse

if TYPE_CHECKING:
    from fastapi import Request

    from app.core.exceptions.http.base import BaseVerboseHTTPException


async def verbose_http_exception_handler(
    _: 'Request',
    exc: 'BaseVerboseHTTPException',
) -> JSONResponse:
    """Обработчик кастомных исключений, выбрасываемых вручную."""
    return JSONResponse(status_code=exc.status_code, content=exc.as_dict(), headers=exc.headers)
