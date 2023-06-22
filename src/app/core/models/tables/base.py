"""Модуль базовых таблиц моделей данных проекта."""
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel
from sqlalchemy import BigInteger
from sqlalchemy.orm import DeclarativeBase, mapped_column

from app.core.config import logger

if TYPE_CHECKING:
    from sqlalchemy.orm import Mapped

ATTR_NOT_FOUND_TEMPLATE = 'Атрибут "{field}" не был найден в модели {class_name}.'


class Base(DeclarativeBase):
    """Базовый класс для объявления моделей SQLAlchemy."""

    __abstract__ = True

    default_include_fields: tuple[str] | None = None
    default_replace_fields: dict[str, str] | None = None

    id: 'Mapped[int]' = mapped_column(  # noqa: A003
        BigInteger,
        nullable=False,
        unique=True,
        primary_key=True,
        autoincrement=True,
    )

    def _get_model_attr(self: 'Base', field: str) -> Any:  # noqa: ANN401
        """Достает атрибут модели по его имени.

        Parameters
        ----------
        field
            поле модели.

        Returns
        -------
        Any
            любое значение поля модели.
        """
        value = self
        for field_part in field.split('.'):
            value = getattr(value, field_part, None)
            if callable(value):
                value = value()
        return value

    def _add_by_includes(
        self: 'Base',
        item: dict[str, Any],
        *include: str,
    ) -> None:
        """Добавляет значения include для item'а.

        Parameters
        ----------
        item
            словарь для заполнения результата.
        include
            поля модели.

        Raises
        ------
        AttributeError
            переписанное описание ошибки, которая была поймана при получении атрибутов.
        """
        for variable_name in include:
            try:
                value = self._get_model_attr(variable_name)
            except AttributeError as exc:
                logger.warning('Атрибут %s не найден.', variable_name)
                msg = (
                    'Параметр include должен содержать названия полей модели. '
                    f'Атрибут {variable_name} не найден!'
                )
                raise AttributeError(msg) from exc
            item[variable_name] = value

    def _replace(
        self: 'Base',
        item: dict[str, Any],
        **replace: str,
    ) -> None:
        """Устанавливает другие значения для элементов item'а (alias).

        Parameters
        ----------
        item
            словарь для заполнения результата.
        replace
            поля модели для замены.

        Raises
        ------
        AttributeError
            переписанное описание ошибки, которая была поймана при получении атрибутов.
        """
        for original, replaced in replace.items():
            try:
                value_to_replace = self._get_model_attr(replaced)
            except AttributeError as exc:
                logger.warning('Атрибут %s не найден.', replaced)
                msg = (
                    'Параметр replace должен содержать пару "оригинальное поле"-"новое поле" '
                    f'модели. Атрибут "{replaced}" не найден'
                )
                raise AttributeError(msg) from exc
            item[original] = value_to_replace

    def as_dict(
        self: 'Base',
        *include: str,
        **replace: str,
    ) -> dict[str, Any]:
        """Базовый метод для всех моделей, возвращающий словарь значений.

        Parameter
        ---------
        include
            поля модели.
        replace
            поля модели для замены.

        Returns
        -------
        dict[str, Any]
            итоговый словарь, репрезентирующий модель данных.

        Raises
        ------
        AttributeError
            переписанное описание ошибки, которая была поймана при получении атрибутов.
        """
        item: dict[str, Any] = {}
        if not include and self.default_include_fields is not None:
            include = self.default_include_fields
        self._add_by_includes(item, *include)
        if not replace and self.default_replace_fields is not None:
            replace = self.default_replace_fields
        self._replace(item, **replace)
        return item

    def _is_dict_different_from(
        self: 'Base',
        item: dict[str, Any],
    ) -> bool:
        """Проверка экземпляра модели на соответствие с переданным словарём.

        Parameters
        ----------
        item
            словарь, с которым будет сравниваться self.

        Returns
        -------
        bool
            является ли сравниваемый объект сходим с pydantic-моделью.

        Raises
        ------
        AttributeError
            выбрасывается, когда атрибут не присутствует в модели данных self.
        """
        for field, value in item.items():
            if not hasattr(self, field):
                msg = ATTR_NOT_FOUND_TEMPLATE.format(
                    field=field,
                    class_name=self.__class__.__name__,
                )
                raise AttributeError(msg)
            try:
                self_field_value = getattr(self, field)
            except AttributeError as exc:
                msg = ATTR_NOT_FOUND_TEMPLATE.format(
                    field=field,
                    class_name=self.__class__.__name__,
                )
                raise AttributeError(msg) from exc
            if self_field_value != value:
                return True
        return False

    def _is_pydantic_different_from(
        self: 'Base',
        item: BaseModel,
    ) -> bool:
        """Проверка экземпляра модели на соответствие с переданной pydantic-моделью.

        Parameters
        ----------
        item
            объект схемы, с которым будет сравниваться self.

        Returns
        -------
        bool
            является ли сравниваемый объект сходим с pydantic-моделью.

        Raises
        ------
        AttributeError
            выбрасывается, когда атрибут не присутствует в модели данных self.
        """
        item_dict = item.dict()
        return self._is_dict_different_from(item_dict)

    def _is_model_different_from(self: 'Base', item: 'Base') -> bool:
        """Проверка экземпляра модели на соответствие с переданным экземпляром модели.

        Если был передан экземпляр не той же модели, что у `self`, вернется False в любом случае.

        Parameters
        ----------
        item
            объект модели, с которым будет сравниваться self.

        Returns
        -------
        bool
            является ли сравниваемый объект сходим с другим объектом модели.
        """
        if type(item) != type(self):  # type: ignore
            return False
        item_dict = {col.name: getattr(item, col.name) for col in item.__table__.columns}
        self_dict = {col.name: getattr(self, col.name) for col in self.__table__.columns}
        for field, value in item_dict.items():
            self_field_value = self_dict[field]
            if self_field_value != value:
                return True
        return False

    def is_different_from(
        self: 'Base',
        item: 'dict[str, Any] | BaseModel | Base',
    ) -> bool:
        """Проверка экземпляра модели на соответствие с переданными данными.

        Parameters
        ----------
        item
            объект, с которым будет сравниваться self.

        Returns
        -------
        bool
            является ли сравниваемый объект сходим с искомым.

        Raises
        ------
        TypeError
            выбрасывается, когда был передан невалидный тип аргумента `item`.
        AttributeError
            выбрасывается, когда атрибут не присутствует в модели данных self.
        """
        if isinstance(item, BaseModel):
            return self._is_pydantic_different_from(item)
        if isinstance(item, self.__class__):
            return self._is_model_different_from(item)
        if isinstance(item, dict):  # type: ignore
            return self._is_dict_different_from(item)
        msg = (
            'Был передан item неправильного типа данных. '
            f'Ожидались: Dict, BaseModel, Base. Пришёл: {type(item)}.'
        )
        raise TypeError(msg)
