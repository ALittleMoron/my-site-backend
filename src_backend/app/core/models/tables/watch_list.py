from typing import Any

from tortoise import fields
from tortoise.contrib.postgres.indexes import GinIndex

from app.core.models.enums.watch_list import AnimeKindEnum, KinopoiskKindEnum, StatusEnum
from app.core.models.tables.base import Base, TimedMixin
from app.core.models.validators.watch_list import ScoreValidator

KIND_NOT_SET_MESSAGE = 'Сделайте атрибут "kind" полем модели (CharField).'


class WatchListElementBase(TimedMixin, Base):
    """Базовый класс элемента списка просмотренного."""

    kind = None  # Установить в качестве CharField с ENUM-выборами.

    name = fields.CharField(
        max_length=255,
        null=False,
        description='Название',
    )
    native_name = fields.CharField(
        max_length=255,
        null=True,
        description='Название на языке оригинала',
    )
    description = fields.TextField(
        null=True,
        description='Описание',
    )
    my_opinion = fields.TextField(
        null=True,
        description='Моё мнение',
    )
    score = fields.SmallIntField(
        null=True,
        validators=[ScoreValidator],
        description='Оценка',
    )
    repeat_view_count = fields.IntField(
        null=False,
        default=0,
        description='Количество повторных просмотров/прочтений',
    )
    status = fields.CharEnumField(
        StatusEnum,
        max_length=20,
        null=False,
        default=StatusEnum.SCHEDULED,
        description='Статус',
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

    class Meta:  # type: ignore
        """Мета-класс базового абстрактного класса."""

        abstract = True


class Anime(WatchListElementBase):
    """Модель аниме."""

    kind = fields.CharEnumField(
        AnimeKindEnum,
        max_length=10,
        null=False,
        default=AnimeKindEnum.NOT_SET,
        description='вид аниме',
    )

    class Meta:  # type: ignore
        """Мета-класс базового абстрактного класса."""

        table = 'anime_watch_list'
        indexes = [
            GinIndex(fields={'name', 'description'}),
        ]
        ordering = ['-score', 'kind']


class Kinopoisk(WatchListElementBase):
    """Модель контента с Кинопоиска (фильмы, сериалы и мультики, кроме аниме)."""

    kind = fields.CharEnumField(
        KinopoiskKindEnum,
        max_length=18,
        null=False,
        default=KinopoiskKindEnum.NOT_SET,
        description='вид контента с Кинопоиска',
    )

    class Meta:  # type: ignore
        """Мета-класс базового абстрактного класса."""

        table = 'kinopoisk_watch_list'
        indexes = [
            GinIndex(fields={'name', 'description'}),
        ]
        ordering = ['-score', 'kind']
