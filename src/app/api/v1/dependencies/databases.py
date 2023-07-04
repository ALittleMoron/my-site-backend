from typing import TYPE_CHECKING, TypeVar

from fastapi import Depends

from app.core.meta import Session as AppSession

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator, Callable

    from sqlalchemy.ext.asyncio import AsyncSession

    from app.db.repositories.base import BaseRepository

    Repo = TypeVar('Repo', bound=BaseRepository)


async def get_session() -> 'AsyncGenerator[AsyncSession, None]':
    """Генератор получения сессии БД."""
    session = AppSession()
    try:
        yield session
    finally:
        await session.close()


def get_repository(repo_type: 'type[Repo]') -> 'Callable[[AsyncSession], Repo]':
    """Depends, отвечающее за возврат нужного репозитория по его классу."""

    def _get_repo(session: 'AsyncSession' = Depends(get_session)) -> 'Repo':
        """Инициализирует класс репозитория."""
        return repo_type(session)

    return _get_repo
