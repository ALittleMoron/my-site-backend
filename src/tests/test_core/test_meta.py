from sqlalchemy.ext.asyncio.engine import AsyncEngine
from sqlalchemy.ext.asyncio.session import async_sessionmaker

from app.core import meta


def test_is_meta_async() -> None:
    """Проверка на то, что подключение к базе данных является асинхронным."""
    assert isinstance(meta.engine, AsyncEngine)
    assert isinstance(meta.Session, async_sessionmaker)
