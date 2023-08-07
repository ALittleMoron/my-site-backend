"""Точка входа в проект."""
import pathlib
import sys

from fastapi import FastAPI
from sqladmin import Admin

sys.path.insert(0, pathlib.Path(__file__).absolute().parent.parent.as_posix())

from app.admin.auth import authentication_backend
from app.admin.views import all_views
from app.api.v1.api import api_v1_router
from app.core.config import get_application_settings, get_logger
from app.core.exceptions.handlers import verbose_http_exception_handler
from app.core.exceptions.http.base import BaseVerboseHTTPException
from app.core.meta import engine
from app.utils.admin import admin_bulk_add_views

logger = get_logger('app')


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
    admin = Admin(app=app, engine=engine, authentication_backend=authentication_backend)
    admin_bulk_add_views(admin, all_views)

    return app
