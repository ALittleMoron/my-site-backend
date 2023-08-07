from string import Template
from typing import Any, Self, TypedDict

from abstractcp import Abstract, abstract_class_property
from fastapi import HTTPException, status

ABSTRACT_PROPERTY_DEFAULT_VALUE = '<abstract property>'


class VerboseHTTPExceptionDict(TypedDict):
    """Типизированный словарь кастомного базового исключения."""

    code: str
    type: str  # noqa: A003
    message: str
    loc: str | None
    attr: str | None


class BaseHTTPException(HTTPException):
    """Класс HTTP-исключения со status_code по умолчанию."""

    headers: dict[str, Any] | None = None
    status_code: int = status.HTTP_400_BAD_REQUEST

    def __init__(
        self: 'BaseHTTPException',
    ) -> None:
        super().__init__(status_code=self.status_code)


class BaseVerboseHTTPException(BaseHTTPException, Abstract):
    """Базовый класс HTTP-исключения для вывода более подробной информации."""

    code: str = abstract_class_property(str)
    type_: str = abstract_class_property(str)
    message: str = abstract_class_property(str)
    loc: str | None = None
    template: Template | str | None = None
    attr: str | None = None

    def __init__(  # noqa: D105
        self: Self,
        *,
        attr_name: str | None = None,
        loc: str | None = None,
        message: str | None = None,
        template: Template | str | None = None,
        headers: dict[str, Any] | None = None,
        **mapping: object,
    ) -> None:
        if attr_name:
            self.attr_name = attr_name
        if loc:
            self.loc = loc
        if message:
            self.message = message
        if template:
            self.template = template
        if mapping and isinstance(self.template, Template):
            self.message = self.template.safe_substitute(**mapping)
        elif mapping and isinstance(self.template, str):
            self.message = self.template.format(**mapping)
        self.headers = headers

    def _get_attribute(self: Self, name: str) -> Any:  # noqa: ANN401
        """Безопасно отдает атрибут экземпляра класса исключения."""
        try:
            return repr(getattr(self, name))
        except Exception:
            return ABSTRACT_PROPERTY_DEFAULT_VALUE

    def __repr__(self: Self) -> str:  # noqa: D105
        cls_name = self.__class__.__name__
        attrs = (
            f'status_code={self.status_code}, code={self._get_attribute("code")}, '
            f'type={self._get_attribute("type_")}, message={self._get_attribute("message")}, '
            f'loc={self.loc}, template={self.template}, attr={self.attr}'
        )
        return f'{cls_name}({attrs})'

    def __str__(self: Self) -> str:  # noqa: D105
        try:
            return self.message
        except Exception:
            return ABSTRACT_PROPERTY_DEFAULT_VALUE

    def from_template(
        self: Self,
        **mapping: object,
    ) -> Self:
        """Заполняет шаблон и возвращает класс с сообщением в виде заполненного шаблона.

        Пример использования:
        ```
        class SomeClass(BaseVerboseHTTPException):
            code = 'abc'
            type_ = 'abc'
            message = 'abc'
            template = Template('abc with template : $abc')

        ```

        Исходя из определения класса выше, сообщение будет следующее:

        >>> SomeClass.from_template(abc='25).message
        'abc with template : 25'

        Если бы шаблон не был определен, то на месте сообщения была бы строка ``'abc'``.
        """
        if isinstance(self.template, Template):
            self.message = self.template.safe_substitute(**mapping)
        elif isinstance(self.template, str):
            self.message = self.template.format(**mapping)
        return self

    def with_attr(self: Self, attr_name: str) -> Self:
        """Добавляет поле атрибута в класс исключения.

        Пример использования:
        ```
        class SomeClass(BaseVerboseHTTPException):
            code = 'abc'
            type_ = 'abc'
            message = 'abc'

        ```

        Исходя из определения класса выше, сообщение будет следующее:

        >>> SomeClass.with_attr('attr').attr
        'attr'
        """
        self.attr = attr_name
        return self

    def with_loc(self: Self, loc: str) -> Self:
        """Добавляет поле расположения в класс исключения.

        Пример использования:
        ```
        class SomeClass(BaseVerboseHTTPException):
            code = 'abc'
            type_ = 'abc'
            message = 'abc'

        ```

        Исходя из определения класса выше, сообщение будет следующее:

        >>> SomeClass.with_loc('loc').loc
        'loc'
        """
        self.loc = loc
        return self

    def as_dict(
        self: Self,
        attr_name: str | None = None,
        loc: str | None = None,
        **mapping: object,
    ) -> VerboseHTTPExceptionDict:
        """Конвертирует исключение в словарь.

        Пример использования:
        ```
        class SomeClass(BaseVerboseHTTPException):
            code = 'abc'
            type_ = 'abc'
            message = 'abc'
            template = Template('abc with template : $abc')

        ```

        Исходя из определения класса выше, сообщение будет следующее:

        >>> SomeClass.from_template(abc='25).with_attr('my_attr).as_dict()
        {"code": "abc", "type": "abc", "message": "abc with template : 25", "attr": "my_attr"}
        """
        if mapping:
            self = self.from_template(**mapping)
        if attr_name:
            self = self.with_attr(attr_name)
        if loc:
            self = self.with_loc(loc)
        return {
            "code": self.code,
            "type": self.type_,
            "message": self.message,
            "loc": self.loc,
            "attr": self.attr,
        }
