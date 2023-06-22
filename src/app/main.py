"""Точка входа в проект."""
import pathlib
import sys

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

sys.path.insert(0, a := pathlib.Path(__file__).absolute().parent.parent.as_posix())

from app.api.v1.api import api_v1_router  # noqa: E402
from app.core.config import get_application_settings  # noqa: E402


def add_custom_openapi(app: FastAPI) -> None:
    """Устанавливает описание в документации отличное от изначального от fastapi.

    Parameters
    ----------
    app
        экземпляр приложения FastAPI.

    """
    with (pathlib.Path(__file__).parent / 'openapi_description.md').open(mode='r') as reader:
        description = reader.read()
    openapi_schema = get_openapi(
        title='',
        version='0.0.1',
        description=description,
        routes=app.routes,
    )

    app.openapi_schema = openapi_schema


def get_application() -> FastAPI:
    """Подготавливает экземпляр приложения для запуска.

    Returns
    -------
    FastAPI
        экземпляр приложения.
    """
    app_settings = get_application_settings()

    app = FastAPI(**app_settings.fastapi_kwargs)
    app.include_router(api_v1_router)

    add_custom_openapi(app)

    return app
