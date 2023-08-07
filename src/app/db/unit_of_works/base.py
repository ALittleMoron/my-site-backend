from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Self

from app.core.config import get_logger
from app.core.meta import Session as DefaultSessionFactory

if TYPE_CHECKING:
    from types import TracebackType

    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker


logger = get_logger('app')


class BaseUnitOfWork(ABC):
    """Класс единицы работы бизнес-логики."""

    session: 'AsyncSession'

    def __init__(
        self: Self,
        session_factory: 'async_sessionmaker[AsyncSession]' = DefaultSessionFactory,
    ) -> None:
        self._session_factory = session_factory

    async def __aenter__(self: Self) -> Self:
        """Асинхронный вход в контекстный менеджер единицы работы бизнес-логики."""
        self.session = self._session_factory()
        # NOTE: прокидываем сессию явно, чтобы иметь возможность использовать метод без with
        self.init_repositories(self.session)
        return self

    async def __aexit__(
        self: Self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: 'TracebackType | None',
    ) -> None:
        """Асинхронный выход из контекстного менеджера единицы работы бизнес-логики."""
        if exc:
            logger.error('UNIT-OF-WORK E0: %s', exc)
        await self.rollback()
        await self.close()

    @abstractmethod
    def init_repositories(self: Self, session: 'AsyncSession') -> None:
        """Инициализирует классы репозиториев, переданные."""
        raise NotImplementedError()

    async def commit(self: Self) -> None:
        """Фиксирует изменения транзакции в базе данных (alias к ``commit`` сессии)."""
        if not self.session:
            # NOTE: на случай, если класс был использован не через with
            return
        await self.session.commit()

    async def rollback(self: Self) -> None:
        """Откатывает изменения транзакции в базе данных (alias к ``rollback`` сессии)."""
        if not self.session:
            # NOTE: на случай, если класс был использован не через with
            return
        await self.session.rollback()

    async def close(self: Self) -> None:
        """Закрывает сессию (alias к ``close`` сессии.)."""
        if not self.session:
            # NOTE: на случай, если класс был использован не через with
            return
        await self.session.close()
