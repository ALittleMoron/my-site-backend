import asyncio
import pathlib
import sys
from logging.config import fileConfig
from typing import TYPE_CHECKING, Any

from alembic import context
from sqlalchemy import create_engine
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import AsyncEngine

sys.path.insert(0, (pathlib.Path(__file__).absolute().parent.parent).as_posix())

from app.core.config import get_database_settings  # noqa: E402
from app.core.models.tables.base import Base  # noqa: E402

if TYPE_CHECKING:
    from alembic.config import Config

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# ... etc.


def get_config_variable_as_list(config: 'Config', key: str) -> list[str] | None:
    """Parse `alembic` segment of alembic.ini file for given key.

    Parameters
    ----------
    config
        object of alembic config.
    key
        name of variable in alembic.ini config.

    Returns
    -------
    list[str] | None
        parsed segment as list of None.
    """
    arr = config.get_main_option(key, None)
    if arr is None:
        return arr
    return [token for a in arr.split('\n') for b in a.split(',') if (token := b.strip())]


exclude_tables = get_config_variable_as_list(config, "exclude_tables")


def is_object_included(_, name: str, type_: str, *__: Any, **___: Any) -> bool:  # noqa
    """Custom filter function for inner alembic use.

    Check if table in `exclude tables` variable: if table name in `exclude_tables`, don't pass it in
    autogenerated migrations, else pass.

    Parameters
    ----------
    name (str): name of including object.
    type_ (str): type of including object (table, enum, etc.)
    __ (Any): Not using args.
    ___ (Any): not using kwargs.

    Returns
    -------
    bool
        flag of passing in migrations.
    """  # noqa
    return exclude_tables is None or not (type_ == 'table' and name in exclude_tables)


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = get_database_settings().db_url
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        include_object=is_object_included,  # type: ignore
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """Do run migrations.

    Parameters
    ----------
    connection
        engine connection.
    """
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    engine = create_engine(get_database_settings().db_url)
    connectable = AsyncEngine(engine)

    async with connectable.connect() as connection:
        context.configure(
            connection=connection,  # type: ignore
            target_metadata=target_metadata,
            include_object=is_object_included,  # type: ignore
        )
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
