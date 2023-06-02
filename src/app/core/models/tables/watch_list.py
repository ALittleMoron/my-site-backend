"""Модуль таблиц списка просмотренного/прочитанного/наигранного."""
from typing import Any

from sqlalchemy import CheckConstraint, Enum, Integer, SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.models.enums import watch_list as watch_list_enums
from app.core.models.mixins.time import TimeMixin
from app.core.models.tables.base import Base

KIND_NOT_SET_MESSAGE = 'Сделайте атрибут "kind" полем модели (CharField).'
WATCH_LIST_ELEMENT_NAME_LENGTH = 255
WATCH_LIST_ELEMENT_NATIVE_NAME_LENGTH = 255


class WatchListElementBase(TimeMixin, Base):
    """Базовый класс элемента списка просмотренного."""

    __abstract__ = True
    __table_args__ = (
        CheckConstraint('score >= 0'),
        CheckConstraint('score <= 100'),
    )

    kind = None  # Установить в качестве ENUM.

    name: Mapped[str] = mapped_column(
        String(WATCH_LIST_ELEMENT_NAME_LENGTH),
        nullable=False,
        doc='Название',
    )
    native_name: Mapped[str] = mapped_column(
        String(WATCH_LIST_ELEMENT_NAME_LENGTH),
        nullable=False,
        doc='Название на языке оригинала',
    )
    description: Mapped[str] = mapped_column(
        String,
        nullable=True,
        doc='Описание',
    )
    my_opinion: Mapped[str] = mapped_column(
        String,
        nullable=True,
        doc='Моё мнение',
    )
    score: Mapped[int] = mapped_column(
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

    def __init__(self, **kwargs: dict[str, Any]) -> None:
        """Init базового класса с проверкой на то, что поле kind установлено.

        Args:
            kwargs: дополнительные параметры.

        Raises:
            NotImplementedError: выкидывается, если атрибут kind не был установлен в качестве поля.
        """
        if self.kind is None:
            raise NotImplementedError(KIND_NOT_SET_MESSAGE)
        super().__init__(**kwargs)


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
