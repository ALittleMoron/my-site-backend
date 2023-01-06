"""Django-like manage.py script for some administration utils."""
import sys

from typer import Typer

from app.core import settings as _  # noqa: F401
from app.management.app import build_application
from app.management.collector import Collector
from app.management.exceptions import BaseManagementError

typer = Typer()
collector = Collector()
application = build_application(app=typer, collector=collector)


def main():
    """Точка входа в CLI-приложение."""
    try:
        application()
    except BaseManagementError as e:
        sys.stdout.write(str(e) + "\n")
        sys.exit(87)


if __name__ == "__main__":
    main()
