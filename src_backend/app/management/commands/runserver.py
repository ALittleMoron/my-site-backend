import os
from typing import Optional

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
        workers: Optional[int] = 4,
        mode: str = 'dev',
    ):
        """Команда запуска локального тестового сервера."""
        if not host or not port or not workers or not mode or mode not in {'dev', 'prod'}:
            raise IncorrectParametersError
        if mode == 'dev':
            workers = None
            reload = True
            delay = 1
        else:
            reload = False
            delay = 0.25
        os.environ['PROJECT_RUN_MODE'] = mode
        uvicorn.run(  # type: ignore
            'app.main:get_application',
            host=host,
            port=port,
            reload=reload,
            reload_delay=delay,
            workers=workers,
            factory=True,
        )


command = Runserver()
