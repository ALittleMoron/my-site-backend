import subprocess
import sys

import typer

from .base import AbstractBaseCommand

LOWEST_COVERAGE_PERCENT = '80'


class Coverage(AbstractBaseCommand):
    """Класс-команда, выполняющая запуск проверку тестов на охват."""

    def action(self):
        """Команда запуска проверки охвата проекта тестами."""
        subprocess.check_call(
            ['coverage', 'run', '--rcfile', './pyproject.toml', '-m', 'pytest', './tests'],
        )
        try:
            subprocess.check_call(
                ['coverage', 'report', '--fail-under', LOWEST_COVERAGE_PERCENT],
            )
        except subprocess.CalledProcessError:
            message = typer.style(
                f'\nТесты не охватывают нужный процент кода ({LOWEST_COVERAGE_PERCENT}).',
                fg=typer.colors.RED,
            )
            typer.echo(
                message,
                color=True,
            )
            sys.exit(2)


command = Coverage()
