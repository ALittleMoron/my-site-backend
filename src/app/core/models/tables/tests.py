import datetime
import uuid

from sqlalchemy import UUID, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.models.mixins.ids import UUIDMixin
from app.core.models.mixins.time import TimeMixin
from app.core.models.tables import Base
from app.core.models.types.datetime import UTCDateTime


class TestBaseModel(Base, UUIDMixin, TimeMixin):
    """Тестовая модель для проверки работы абстрактных данных в вакууме.

    Гарантирует, что базовые методы работы с моделями будут работать всегда так, как нужно.
    """

    __test__ = False  # pytest collect skip
    __tablename__ = '__test_model__'

    text: Mapped[str | None] = mapped_column(String)
    disabled_at: Mapped[datetime.datetime | None] = mapped_column(UTCDateTime)
    test_related_models: Mapped[list['TestRelatedModel']] = relationship(
        uselist=True,
        back_populates='test_base_model',
        lazy='selectin',
    )


class TestRelatedModel(Base, UUIDMixin, TimeMixin):
    """Тестовая модель для работы отношений между моделями."""

    __test__ = False  # pytest collect skip
    __tablename__ = '__test_related_model__'

    text: Mapped[str | None] = mapped_column(String)
    disabled_at: Mapped[datetime.datetime | None] = mapped_column(UTCDateTime)
    test_base_model_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('__test_model__.id', ondelete='CASCADE'),
        nullable=False,
    )
    test_base_model: Mapped['TestBaseModel'] = relationship(
        uselist=False,
        back_populates='test_related_models',
        lazy='selectin',
    )
