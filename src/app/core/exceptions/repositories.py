class BaseRepositoryError(Exception):
    """Базовое исключение репозитория."""


class RepositoryAttributeError(BaseRepositoryError):
    """Исключение, связанное с ошибкой атрибута в классе репозитория."""


class RepositoryBaseMethodAccessError(RepositoryAttributeError):
    """Исключение, связанные с некорректным вызовом базовых методов репозитория."""


class RepositorySubclassNotSetAttributeError(RepositoryAttributeError):
    """Исключение, связанное с тем, что в дочернем классе не был установлен нужный атрибут."""
