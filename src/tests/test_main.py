from fastapi import FastAPI

from app import main
from app.core.exceptions.http.base import BaseVerboseHTTPException
from app.core.settings import base as base_settings


def test_app_description_set() -> None:
    """Проверка описания документации FastAPI и функции get_application."""
    app = main.get_application()
    assert isinstance(app, FastAPI)
    with (base_settings.APP_DIR / 'openapi_description.md').open(mode='r') as reader:
        description = reader.read()
    assert app.description == description
    assert BaseVerboseHTTPException in app.exception_handlers
