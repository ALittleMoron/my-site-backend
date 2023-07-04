"""Точка входа в проект."""
import pathlib
import sys

from fastapi import FastAPI

sys.path.insert(0, pathlib.Path(__file__).absolute().parent.parent.as_posix())

from app.api.v1.api import api_v1_router
from app.core.config import get_application_settings
from app.core.exceptions.handlers import verbose_http_exception_handler
from app.core.exceptions.http.base import BaseVerboseHTTPException


def get_application() -> FastAPI:
    """Подготавливает экземпляр приложения для запуска.

    Returns
    -------
    FastAPI
        экземпляр приложения.
    """
    app_settings = get_application_settings()

    with app_settings.path_to_description.open(mode='r') as reader:
        description = reader.read()
    app = FastAPI(description=description, **app_settings.fastapi_kwargs)
    app.include_router(api_v1_router)
    app.add_exception_handler(  # type: ignore
        BaseVerboseHTTPException,
        verbose_http_exception_handler,
    )

    return app
