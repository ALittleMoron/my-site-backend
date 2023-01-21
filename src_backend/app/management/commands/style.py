import subprocess
import sys

from .base import AbstractBaseCommand


class CheckStyles(AbstractBaseCommand):
    """Класс-команда, выполняющая запуск проверку стилей проекта."""

    def action(self):
        """Команда запуска проверки стилей проекта..."""
        print('\nЗапускаем проверку стилей для приложения...')  # noqa: T201
        app_return_status = subprocess.run(('flake8', 'app'))
        print('\nЗапускаем проверку стилей для тестов...')  # noqa: T201
        tests_return_status = subprocess.run(('flake8', 'tests'))
        if app_return_status.returncode | tests_return_status.returncode:
            sys.exit(1)
        print('\n-----------------\nВсе проверки стилей успешно пройдены')  # noqa: T201
        sys.exit(0)


command = CheckStyles()
