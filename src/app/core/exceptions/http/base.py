from string import Template
from typing import TYPE_CHECKING, Any, TypedDict, TypeVar

from abstractcp import Abstract, abstract_class_property
from fastapi import HTTPException, status

if TYPE_CHECKING:
    Templated = TypeVar('Templated', bound='BaseVerboseHTTPException')


class VerboseHTTPExceptionDict(TypedDict):
    """Типизированный словарь кастомного базового исключения."""

    code: str
    type: str  # noqa: A003
    message: str
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
    template: Template | str | None = None
    attr: str | None = None

    @classmethod
    def from_template(
        cls: 'type[Templated]',
        **mapping: object,
    ) -> 'type[Templated]':
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
        if isinstance(cls.template, Template):
            cls.message = cls.template.safe_substitute(**mapping)
        elif isinstance(cls.template, str):
            cls.message = cls.template.format(**mapping)
        return cls

    @classmethod
    def with_attr(cls: 'type[Templated]', attr_name: str) -> 'type[Templated]':
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

        Если бы шаблон не был определен, то на месте атрибута был бы ``None``.
        """
        cls.attr = attr_name
        return cls

    @classmethod
    def as_dict(
        cls: 'type[Templated]',
        attr_name: str | None = None,
        headers: dict[str, Any] | None = None,
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
        if headers:
            cls.headers = headers
        if mapping:
            cls = cls.from_template(**mapping)
        if attr_name:
            cls = cls.with_attr(attr_name)
        return {"code": cls.code, "type": cls.type_, "message": cls.message, "attr": cls.attr}
