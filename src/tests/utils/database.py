from typing import TYPE_CHECKING, Any, TypeVar

from sqlalchemy.exc import SQLAlchemyError

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

    from app.core.models.tables.base import Base

    BaseSQLAlchemyModel = TypeVar('BaseSQLAlchemyModel', bound=Base)


async def db_create_item(
    db_session_factory: 'async_sessionmaker[AsyncSession]',
    model: 'type[BaseSQLAlchemyModel]',
    params: dict[str, Any],
) -> 'BaseSQLAlchemyModel':
    """Создает запись в базе данных из модели и параметров."""
    async with db_session_factory() as db_:
        item = model(**params)
        db_.add(item)
        try:
            await db_.commit()
            await db_.flush()
            await db_.refresh(item)
        except SQLAlchemyError:
            await db_.rollback()
            raise
        else:
            return item
