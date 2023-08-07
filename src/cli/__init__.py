"""Пакет команд для работы с проектом."""
from typing import Annotated, Optional

import typer

from .custom_typers import AsyncTyper

cli = AsyncTyper()
db_cli = AsyncTyper()
admin_cli = AsyncTyper()
cli.add_typer(admin_cli, name='admin', short_help='Команды для работы с админ-панелью.')
cli.add_typer(db_cli, name='db', short_help='Команды для работы с базой данных.')


@cli.async_command()
async def create_admin(username: str, password: str):
    """Создает нового администратора для админ-панели."""
    from .commands.admin import create_admin_command

    await create_admin_command(username, password)


@db_cli.command()
def migrate(revision: Annotated[str, typer.Argument(help='id миграции')] = 'head'):
    """Применяет миграции до переданной.

    Если ничего не передано, обновляется до последней миграции (head).
    """
    from .commands.db import migrate

    migrate(revision=revision)


@db_cli.command()
def revert_migrations(revision: Annotated[str, typer.Argument(help='id миграции')] = 'base'):
    """отменяет миграции до переданной. Если ничего не передано.

    Если ничего не передано, обновляет базу до состояния перед накатыванием всех миграций ("чистая"
    база без миграций).
    """
    from .commands.db import revert_migrations

    revert_migrations(revision=revision)


@db_cli.command()
def make_migration(
    message: Annotated[
        Optional[str],
        typer.Argument(help='название миграции / сообщение в миграции'),
    ] = None,
    auto: Annotated[
        bool,
        typer.Argument(help='сгенерировать миграцию из изменений в моделях?'),
    ] = True,
):
    """Создает миграцию."""
    from .commands.db import make_migration

    make_migration(message=message, autogenerate=auto)
