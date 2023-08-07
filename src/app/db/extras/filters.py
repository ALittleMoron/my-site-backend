from typing import TYPE_CHECKING, Any, Self

from app.core.exceptions.http import filters as filter_http_exceptions
from app.core.exceptions.results import Err
from app.core.schemas.classes.filters import FilterSchema

if TYPE_CHECKING:
    from sqlalchemy.orm.attributes import InstrumentedAttribute

    from app.core.models.tables import Base


class AdvancedFilters:
    """Класс для работы с фильтрацией.

    Фильтрация происходит путем передачи в query-параметрах переменной filters со следующей
    структурой:

        ```
        {
            "field": str,
            "value": Any,
            "operator": str  # enum
        }
        ```
    """

    def validate_filter_fields(
        self: Self,
        *,
        model_class: type['Base'],
        filters: list[FilterSchema],
        extra_field_mapping: 'dict[str, InstrumentedAttribute[Any]] | None' = None,
    ) -> Err[filter_http_exceptions.BaseHttpFilterError] | None:
        """Проверяет переданные фильтры на вхождение полей в модель данных.

        Если тех полей, что переданы в фильтрах, нет в модели, это может привести к ошибкам или
        багам.

        Parameters
        ----------
        model_class
            класс модели для проверки полей.
        filters
            сами фильтры
        extra_field_mapping
            дополнительные правила наложения полей фильтров на поля модели на случай, если есть
            alias в названии или нужно получить поле связанной модели.
        """
        extra_field_mapping_keys = list(extra_field_mapping.keys() if extra_field_mapping else [])
        available_fields = model_class.__table__.columns.keys() + extra_field_mapping_keys
        for filter_ in filters:
            if filter_.field not in available_fields:
                reason = (
                    f'поле "{filter_.field}" не присутствует в таблице {model_class.__tablename__} '
                    f'или нет правила для наложения строки на поле связанной сущности.'
                )
                return Err(
                    filter_http_exceptions.InvalidFilterFieldError().from_template(reason=reason),
                )
