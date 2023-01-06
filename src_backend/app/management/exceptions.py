from app.management import context


class BaseManagementError(Exception):
    """Базовый класс исключения в суб-модуле management."""

    message = None

    def __init__(self, *args: object) -> None:
        """Базовый экземпляр исключения, добавляющий message для вывода.

        Args:
            *args (object): аргументы для вывода.
        """
        if self.message:
            args += (self.message,)
        super().__init__(*args)


# ------------------ validation -----------------------


class BaseValidationError(Exception):
    """Базовый класс исключения во время валидации параметров."""


class IncorrectParametersError(BaseValidationError):
    """Класс исключения некорректных параметров.

    Выкидывается, если были переданы неправильные параметры.
    """

    message = context.NONE_PARAMETERS_PASSED_MESSAGE


# ------------------ validation -----------------------


class BaseExecuteError(BaseManagementError):
    """Базовый класс исключения во время выполнения команды."""


class CollectorExecuteError(BaseExecuteError):
    """Класс исключение коллектора.

    Выкидывается, если во время импорта команд возникла ошибка.
    """
