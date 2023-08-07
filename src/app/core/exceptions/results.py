from typing import Any, Generic, NoReturn, Self, TypeVar, final

Value = TypeVar("Value")
Error = TypeVar("Error", bound=Exception)
DefaultT = TypeVar('DefaultT')


@final
class Ok(Generic[Value]):
    """Класс успешного ответа."""

    _value: Value
    __match_args__ = ('_value',)

    def __init__(self: Self, value: Value) -> None:
        self._value = value

    def __repr__(self: Self) -> str:  # noqa: D105
        return f"Ok({repr(self._value)})"

    def __eq__(self: Self, other: Any) -> bool:  # noqa: D105 ANN401
        if isinstance(other, Ok):
            return self._value == other._value  # type: ignore
        return False

    def err(self: Self) -> None:
        """Отдает None, потому что в Ok нет ошибки."""
        return None

    def unwrap(self: Self) -> Value:
        """Отдает перехваченный успешный ответ."""
        return self._value


@final
class Err(Generic[Error]):
    """Класс ошибки выполнения."""

    _err: Error
    __match_args__ = ('_err',)

    def __init__(self: Self, err: Error) -> None:
        self._err = err

    def __repr__(self: Self) -> str:  # noqa: D105
        return f"Err({repr(self._err)})"

    def __eq__(self: Self, other: Any) -> bool:  # noqa: D105 ANN401
        if isinstance(other, Err):
            return self._err == other._err  # type: ignore
        return False

    def err(self: Self) -> Error:
        """Отдает отловленное исключение без выбрасывания."""
        return self._err

    def unwrap(self: Self) -> NoReturn:
        """Выкидывает отловленное исключение."""
        raise self._err


Result = Ok[Value] | Err[Error]
