import re
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from pydantic_core import CoreSchema, PydanticCustomError, core_schema

if TYPE_CHECKING:
    from pydantic import GetCoreSchemaHandler, GetJsonSchemaHandler
    from pydantic.json_schema import JsonSchemaValue


@dataclass
class Regex:
    """Класс-валидатор типа для регулярного выражения."""

    pattern: str

    def __get_pydantic_core_schema__(  # noqa: D105
        self: 'Regex',
        source_type: Any,  # noqa
        handler: 'GetCoreSchemaHandler',
    ) -> 'CoreSchema':
        regex = re.compile(self.pattern)

        def match(v: str) -> str:
            if not regex.match(v):
                error_type = 'string_pattern_mismatch'
                message_template = "String should match pattern '{pattern}'"
                raise PydanticCustomError(
                    error_type,
                    message_template,
                    {'pattern': self.pattern},
                )
            return v

        return core_schema.no_info_after_validator_function(
            match,
            handler(source_type),
        )

    def __get_pydantic_json_schema__(  # noqa: D105
        self: 'Regex',
        core_schema: 'CoreSchema',
        handler: 'GetJsonSchemaHandler',
    ) -> 'JsonSchemaValue':
        json_schema = handler(core_schema)
        json_schema['pattern'] = self.pattern
        return json_schema
