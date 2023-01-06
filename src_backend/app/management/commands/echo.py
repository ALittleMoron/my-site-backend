from .base import AbstractBaseCommand


class Echo(AbstractBaseCommand):
    """Класс-команда, выполняющая эхо-ответ."""

    def action(self, *, echo: str):
        """Обычная эхо-команда. Ничего не делает, кроме как повторять введенную строку."""  # noqa
        print(echo)  # noqa: T201


command = Echo()
