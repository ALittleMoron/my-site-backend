import os
import pathlib
import sys

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from tortoise.contrib.fastapi import register_tortoise  # type: ignore

if os.environ.get('VSCODE_DEBUG_MODE'):
    sys.path.insert(0, a := pathlib.Path(__file__).absolute().parent.parent.as_posix())

from app.api.v1.api import api_v1_router
from app.core.config import TORTOISE_ORM, get_application_settings


def add_custom_openapi(app: FastAPI):
    """Устанавливает описание в документации отличное от изначального от fastapi.

    Args:
        app (FastAPI): экземпляр приложения FastAPI.
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

    Returns:
        FastAPI: экземпляр приложения.
    """
    app_settings = get_application_settings()

    app = FastAPI(**app_settings.fastapi_kwargs)
    app.include_router(api_v1_router)

    add_custom_openapi(app)

    register_tortoise(
        app,
        config=TORTOISE_ORM,
        generate_schemas=True,
        add_exception_handlers=True,
    )

    return app
