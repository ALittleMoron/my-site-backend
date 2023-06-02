"""Модуль метаданных для работы с базой данных через sqlalchemy."""
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio.session import async_sessionmaker

from app.core.config import get_database_settings
from app.core.settings.base import TESTING_MODE

engine = create_async_engine(get_database_settings().db_url, future=True, echo=TESTING_MODE)
Session = async_sessionmaker(engine, expire_on_commit=False)
