from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy_utils.types.password import PasswordType

from app.core.models.mixins.ids import UUIDMixin
from app.core.models.mixins.time import TimeMixin
from app.core.models.tables.base import Base

USERNAME_LENGTH = 255


class Admin(UUIDMixin, TimeMixin, Base):
    """Администратор."""

    __tablename__ = 'admins'

    username: Mapped[str] = mapped_column(String(USERNAME_LENGTH), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(PasswordType(schemes=['pbkdf2_sha512']))
