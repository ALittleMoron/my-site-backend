"""Пакет для страниц (views) админ-панели."""
from .watch_list import AnimeAdminView, KinopoiskAdminView

all_views = (AnimeAdminView, KinopoiskAdminView)
