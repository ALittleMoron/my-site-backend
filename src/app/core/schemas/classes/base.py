from pydantic import BaseModel, ConfigDict


class DetailScheme(BaseModel):
    """Схема ответа сервера."""

    code: str
    type: str  # noqa: A003
    message: str
    loc: str | None
    attr: str | None


class BaseOrmSchema(BaseModel):
    """Базовый класс ORM-схемы."""

    model_config = ConfigDict(from_attributes=True)
