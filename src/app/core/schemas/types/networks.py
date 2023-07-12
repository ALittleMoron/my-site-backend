"""Модуль дополнительных типов-валидаторов для pydantic-схем, связанных с сетью."""
from typing import Annotated

from annotated_types import MaxLen, MinLen

from app.core.schemas.regexes import networks as network_regexes
from app.core.schemas.types.base import Regex

# Аннотированные типы
Host = Annotated[str, MinLen(4), MaxLen(1000), Regex(network_regexes.host_regex)]
