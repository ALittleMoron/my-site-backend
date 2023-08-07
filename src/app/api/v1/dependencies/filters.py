from typing import Any

from fastapi.encoders import jsonable_encoder
from fastapi.params import Query
from fastapi.responses import JSONResponse
from pydantic import Json, ValidationError

from app.core.exceptions.http import filters as filter_http_exceptions
from app.core.schemas.classes.filters import FilterSchema


def get_filters(
    filters: Json[Any] | None = Query(None, description='Something something'),
) -> list[FilterSchema] | JSONResponse:
    """Зависимость, обрабатывающая перевод фильтров из JSON в схему pydantic."""
    res: list[FilterSchema] = []
    try:
        if isinstance(filters, list):
            for _filter in filters:  # type: ignore
                res.append(FilterSchema.model_validate(_filter))  # type: ignore
        else:
            res.append(FilterSchema.model_validate(filters))  # type: ignore
    except ValidationError as exc:
        raise filter_http_exceptions.FilterValidationError(jsonable_encoder(exc.errors())) from exc
    return res
