import sys

import pytest

from .base import AbstractBaseCommand


class RunTests(AbstractBaseCommand):
    """Класс-команда, выполняющая запуск тестов проекта."""

    def action(self):
        """Команда запуска тестов проекта."""
        sys.exit(pytest.main([]))


command = RunTests()
