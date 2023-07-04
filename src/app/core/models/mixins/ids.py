import uuid

from sqlalchemy import UUID, BigInteger
from sqlalchemy.orm import Mapped, mapped_column


class IntegerIDMixin:
    """Примесь для поля числового уникального идентификатора."""

    id: Mapped[int] = mapped_column(  # noqa: A003
        BigInteger,
        nullable=False,
        unique=True,
        primary_key=True,
        autoincrement=True,
    )


class UUIDMixin:
    """Примесь для поля уникального идентификатора в виде UUID."""

    id: Mapped[uuid.UUID] = mapped_column(  # noqa: A003
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
