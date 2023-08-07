"""Модуль таблиц списка просмотренного/прочитанного/наигранного."""
from sqlalchemy import CheckConstraint, Enum, Integer, SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.models.enums import watch_list as watch_list_enums
from app.core.models.mixins.ids import UUIDMixin
from app.core.models.mixins.time import TimeMixin
from app.core.models.tables.base import Base

KIND_NOT_SET_MESSAGE = 'Сделайте атрибут "kind" полем модели (Enum).'
WATCH_LIST_ELEMENT_NAME_LENGTH = 255
WATCH_LIST_ELEMENT_NATIVE_NAME_LENGTH = 255


class WatchListElementBase(TimeMixin, UUIDMixin, Base):
    """Базовый класс элемента списка просмотренного."""

    __abstract__ = True
    __table_args__ = (
        CheckConstraint('score >= 0'),
        CheckConstraint('score <= 100'),
    )

    kind = None  # Установить в качестве ENUM.

    name: Mapped[str] = mapped_column(
        String(WATCH_LIST_ELEMENT_NAME_LENGTH),
        nullable=True,
        doc='Название',
    )
    native_name: Mapped[str] = mapped_column(
        String(WATCH_LIST_ELEMENT_NAME_LENGTH),
        nullable=True,
        doc='Название на языке оригинала',
    )
    description: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
        doc='Описание',
    )
    my_opinion: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
        doc='Моё мнение',
    )
    score: Mapped[int | None] = mapped_column(
        SmallInteger,
        nullable=True,
        doc='Оценка',
    )
    repeat_view_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default='0',
        doc='Количество повторных просмотров/прочтений',
    )
    status: Mapped[watch_list_enums.StatusEnum] = mapped_column(
        Enum(watch_list_enums.StatusEnum),
        nullable=False,
        default=watch_list_enums.StatusEnum.SCHEDULED,
        server_default=watch_list_enums.StatusEnum.SCHEDULED.name,
        doc='Статус',
    )

    def __init_subclass__(cls: 'type[WatchListElementBase]') -> None:  # noqa: D105
        super().__init_subclass__()
        if cls.kind is None:
            raise NotImplementedError(KIND_NOT_SET_MESSAGE)


class Anime(WatchListElementBase):
    """Модель аниме."""

    __tablename__ = 'anime'

    kind: Mapped[watch_list_enums.AnimeKindEnum] = mapped_column(
        Enum(watch_list_enums.AnimeKindEnum),
        nullable=False,
        default=watch_list_enums.AnimeKindEnum.NOT_SET,
        server_default=watch_list_enums.AnimeKindEnum.NOT_SET.name,
        doc='вид аниме',
    )


class Kinopoisk(WatchListElementBase):
    """Модель контента с Кинопоиска (фильмы, сериалы и мультики, кроме аниме)."""

    __tablename__ = 'kinopoisk'

    kind: Mapped[watch_list_enums.KinopoiskKindEnum] = mapped_column(
        Enum(watch_list_enums.KinopoiskKindEnum),
        nullable=False,
        default=watch_list_enums.KinopoiskKindEnum.NOT_SET,
        server_default=watch_list_enums.KinopoiskKindEnum.NOT_SET.name,
        doc='вид контента с Кинопоиска',
    )
