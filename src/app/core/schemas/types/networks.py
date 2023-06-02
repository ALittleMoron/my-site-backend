"""Модуль дополнительных типов-валидаторов для pydantic-схем, связанных с сетью."""
from pydantic import ConstrainedStr

from app.core.schemas.regexes import networks as network_regexes


class Host(ConstrainedStr):
    """Строка с ограничениями: хост."""

    min_length = 4
    max_length = 1000
    regex = network_regexes.host_regex
