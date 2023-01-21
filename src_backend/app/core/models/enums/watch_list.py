import enum


class StatusEnum(str, enum.Enum):
    """Enum статуса произведения."""

    WATCHED = 'Просмотрено'
    ABANDONED = 'Брошено'
    POSTPONED = 'Отложен'
    SCHEDULED = 'Запланирован'
    REVIEWING = 'Пересматриваю'


class AnimeKindEnum(str, enum.Enum):
    """Enum вида аниме."""

    FILM = 'Фильм'
    SERIES = 'Сериал'
    OVA = 'OVA'
    ONA = 'ONA'
    SPECIAL = 'Спешл'
    NOT_SET = 'Не указано'


class KinopoiskKindEnum(str, enum.Enum):
    """Enum вида контента с Кинопоиска."""

    FILM = 'Фильм'
    SERIES = 'Сериал'
    SHORT_FILM = 'Короткометражка'
    NOT_SET = 'Не указано'
