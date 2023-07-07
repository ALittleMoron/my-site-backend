from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy_utils.types.email import EmailType
from sqlalchemy_utils.types.password import PasswordType

from app.core.models.mixins.ids import UUIDMixin
from app.core.models.mixins.time import TimeMixin
from app.core.models.tables.base import Base


class User(Base, UUIDMixin, TimeMixin):
    """Модель данных пользователя."""

    email: Mapped[str] = mapped_column(EmailType, nullable=False, unique=True)
    password: Mapped[str] = mapped_column(PasswordType(schemes=['pbkdf2_sha512']))
