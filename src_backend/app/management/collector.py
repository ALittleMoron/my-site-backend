import os
from importlib import import_module
from pathlib import Path

from app.management.exceptions import CollectorExecuteError

from .commands.base import AbstractBaseCommand


class Collector:
    """Класс-коллектор, который импортирует все команды из папки commands."""

    def __init__(self) -> None:
        """Init для коллектора."""
        self.exclude_files = {"__init__.py", "base.py", "__pycache__"}

    def collect(self) -> dict[str, AbstractBaseCommand]:
        """Главный метод для получения всех команд из папки commands.

        Raises:
            CollectorExecuteError: выкидывается в результате неудачного импорта команды.

        Returns:
            dict[str, BaseCommand]: словарь с "имя файла-экземпляр команды" ключ-значениями.
        """
        result: dict[str, AbstractBaseCommand] = {}
        sub_module = "commands"
        path = Path(__file__).parent / sub_module
        dir_list = os.listdir(path)

        for _file in filter(lambda x: x not in self.exclude_files, dir_list):
            _file_name = "-".join(_file.split(".")[0:-1])
            try:
                package = import_module(f"app.management.{sub_module}.{_file_name}")
                if not isinstance(package.command, AbstractBaseCommand):
                    continue
                result[_file_name] = package.command
            except ImportError as exc:
                raise CollectorExecuteError(f"У коллектора не получилось открыть {_file}.") from exc
        return result
