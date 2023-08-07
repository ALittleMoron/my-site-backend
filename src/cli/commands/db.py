from alembic import command
from alembic.config import Config

from app.core.config import get_path_settings

path_settings = get_path_settings()

ini_file_path = (path_settings.src_dir / 'alembic.ini').as_posix()


def migrate(*, revision: str = 'head'):
    """Функция-alias для команды ``alembic upgrade``."""
    config = Config(ini_file_path)
    command.upgrade(config, revision)


def revert_migrations(*, revision: str = 'head'):
    """Функция-alias для команды ``alembic downgrade``."""
    config = Config(ini_file_path)
    command.downgrade(config, revision)


def make_migration(*, message: str | None = None, autogenerate: bool = False):
    """Функция-alias для команды ``alembic revision``."""
    config = Config(ini_file_path)
    command.revision(config, message, autogenerate)
