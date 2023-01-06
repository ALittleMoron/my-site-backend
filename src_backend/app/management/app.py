from typer import Typer

from .collector import Collector


def build_application(app: Typer, collector: Collector) -> Typer:
    """Функция, создающая экземпляр CLI-приложение.

    Args:
        app (Typer): экземпляр класса Typer.
        collector (Collector): экземпляр класса Collector.

    Returns:
        Typer: экземпляр класса Typer с предустановленными параметрами.
    """
    for command_name, callback in collector.collect().items():
        app.command(command_name)(callback.action)  # type: ignore

    return app
