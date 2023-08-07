"""Модуль классов схем для работы с тестовыми моделями данных."""
import datetime

from pydantic import BaseModel


class TestBaseCreateModel(BaseModel):
    """Схема для создания базовой модели для тестирования."""

    __test__ = False  # pytest collect skip

    text: str
    disabled_at: datetime.datetime


class TestBaseUpdateModel(BaseModel):
    """Схема для обновления базовой модели для тестирования."""

    __test__ = False  # pytest collect skip

    text: str | None = None
    disabled_at: datetime.datetime | None = None
