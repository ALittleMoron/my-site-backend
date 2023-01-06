import os

import uvicorn

from app.management.exceptions import IncorrectParametersError

from .base import AbstractBaseCommand


class Runserver(AbstractBaseCommand):
    """Класс-команда, выполняющая запуск dev-сервера. Не использовать в продакшене."""

    def action(
        self,
        *,  # noqa
        host: str = "localhost",
        port: int = 8000,
        workers: int = 4,
    ):
        """Команда запуска локального тестового сервера."""
        if not host or not port or not workers:
            raise IncorrectParametersError
        os.environ['PROJECT_RUN_MODE'] = 'dev'
        uvicorn.run(  # type: ignore
            'app.main:get_application',
            host=host,
            port=port,
            reload=True,
            workers=workers,
            factory=True,
        )


command = Runserver()
