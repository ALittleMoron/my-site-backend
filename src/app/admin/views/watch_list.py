"""Модуль страниц (views) списков просмотра в админ-панели."""
import wtforms  # type: ignore
from sqladmin import ModelView

from app.core.models.tables.watch_list import Anime, Kinopoisk
from app.utils.admin import enum_field_verbose


class AnimeAdminView(ModelView, model=Anime):
    """Страница просмотренного аниме."""

    icon = 'fa-solid fa-wheelchair-move'
    can_create = False
    can_edit = True
    can_delete = False
    form_columns = [Anime.my_opinion]
    form_overrides = dict(my_opinion=wtforms.TextAreaField)
    column_formatters = {  # type: ignore
        Anime.status: enum_field_verbose,
        Anime.kind: enum_field_verbose,
    }
    column_searchable_list = [
        Anime.name,
        Anime.native_name,
    ]
    column_sortable_list = [
        Anime.kind,
        Anime.score,
        Anime.repeat_view_count,
        Anime.status,
    ]
    column_list = [
        Anime.id,
        Anime.kind,
        Anime.name,
        Anime.score,
        Anime.repeat_view_count,
        Anime.status,
    ]


class KinopoiskAdminView(ModelView, model=Kinopoisk):
    """Страница просмотренного элементов кинопоиска."""

    icon = 'fa solid fa-film'
    can_create = False
    can_edit = True
    can_delete = False
    form_columns = [Kinopoisk.my_opinion]
    column_formatters = {  # type: ignore
        Kinopoisk.status: enum_field_verbose,
        Kinopoisk.kind: enum_field_verbose,
    }
    column_searchable_list = [
        Kinopoisk.name,
        Kinopoisk.native_name,
    ]
    column_sortable_list = [
        Kinopoisk.kind,
        Kinopoisk.score,
        Kinopoisk.repeat_view_count,
        Kinopoisk.status,
    ]
    column_list = [
        Kinopoisk.id,
        Kinopoisk.kind,
        Kinopoisk.name,
        Kinopoisk.score,
        Kinopoisk.repeat_view_count,
        Kinopoisk.status,
    ]
