from abc import ABC, abstractmethod
from typing import Any


class AbstractBaseCommand(ABC):
    """Абстрактный класс команды для выполнения."""

    @abstractmethod
    def action(self, **kwargs: Any) -> Any:
        """Абстрактный метод, выполняющий команду.

        Args:
            **kwargs (Any): произвольное кол-во позиционных аргументов. Должны быть совместимыми с
                            параметрами модуля typer. В случае необходимости получения конкретных
                            значений или значений по паттерну, валидировать значения внутри самого
                            метода.
        """
        pass
