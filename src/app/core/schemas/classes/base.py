from pydantic import BaseModel


class DetailScheme(BaseModel):
    """Схема ответа сервера."""

    code: str
    type: str  # noqa: A003
    message: str
    attr: str | None
