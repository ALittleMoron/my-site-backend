"""Модуль базовых таблиц моделей данных проекта."""
from typing import Any, Optional, Union

from pydantic import BaseModel
from sqlalchemy import BigInteger, Column
from sqlalchemy.orm import DeclarativeBase

from app.core.config import logger


class Base(DeclarativeBase):
    """Базовый класс для объявления моделей SQLAlchemy."""

    __abstract__ = True

    default_include_fields: Optional[tuple[str]] = None
    default_replace_fields: Optional[dict[str, str]] = None

    id = Column(  # noqa: VNE003
        BigInteger,
        nullable=False,
        unique=True,
        primary_key=True,
        autoincrement=True,
    )

    def _get_model_attr(self, field: str) -> Any:
        """Достает атрибут модели по его имени.

        Args:
            field (str): поле модели.

        Returns:
            Any: любое значение поля модели.
        """
        value = self
        for field_part in field.split('.'):
            value = getattr(value, field_part, None)
            if callable(value):
                value = value()
        return value

    def _add_by_includes(
        self,
        item: dict[str, Any],
        *include: str,
    ):
        """Добавляет значения include для item'а.

        Args:
            item (dict[str, Any]): словарь для заполнения результата.
            *include (str): поля модели.

        Raises:
            AttributeError: переписанное описание ошибки, которая была поймана при получении
                            атрибутов.
        """
        for variable_name in include:
            try:
                value = self._get_model_attr(variable_name)
            except AttributeError:
                logger.warning('Атрибут %s не найден.', variable_name)
                raise AttributeError(  # noqa: TC200
                    f'Параметр include должен содержать названия полей модели. '
                    f'Атрибут {variable_name} не найден!',
                )
            item[variable_name] = value

    def _replace(
        self,
        item: dict[str, Any],
        **replace: str,
    ):
        """Устанавливает другие значения для элементов item'а (alias).

        Args:
            item (dict[str, Any]): словарь для заполнения результата.
            **replace (str): поля модели для замены.

        Raises:
            AttributeError: переписанное описание ошибки, которая была поймана при получении
                            атрибутов.
        """
        for original, replaced in replace.items():
            try:
                value_to_replace = self._get_model_attr(replaced)
            except AttributeError:
                logger.warning('Атрибут %s не найден.', replaced)
                raise AttributeError(  # noqa: TC200
                    f'Параметр replace должен содержать пару "оригинальное поле"-"новое поле" '
                    f'модели. Атрибут "{replaced}" не найден',
                )
            item[original] = value_to_replace

    def as_dict(
        self,
        *include: str,
        **replace: str,
    ) -> dict[str, Any]:
        """Базовый метод для всех моделей, возвращающий словарь значений.

        Args:
            *include (str): поля модели.
            **replace (str): поля модели для замены.

        Returns:
            dict[str, Any]: итоговый словарь, репрезентирующий модель данных.
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
        self,
        item: dict[str, Any],
    ) -> bool:
        """Проверка экземпляра модели на соответствие с переданным словарём.

        Args:
            item (BaseModel): объект, с которым будет сравниваться self.

        Returns:
            bool: является ли сравниваемый объект сходим с pydantic-моделью.
        """
        for field, value in item.items():
            if not hasattr(self, field):
                return True
            self_field_value = getattr(self, field)
            if self_field_value != value:
                return True
        return False

    def _is_pydantic_different_from(
        self,
        item: BaseModel,
    ) -> bool:
        """Проверка экземпляра модели на соответствие с переданной pydantic-моделью.

        Args:
            item (BaseModel): объект, с которым будет сравниваться self.

        Returns:
            bool: является ли сравниваемый объект сходим с pydantic-моделью.
        """
        item_dict = item.dict()
        return self._is_dict_different_from(item_dict)

    def _is_model_different_from(
        self,
        item: 'Base',
        # TODO: переделать без *args, **kwargs
        *as_dict_args: str,
        **as_dict_kwargs: str,
    ) -> bool:
        """Проверка экземпляра модели на соответствие с переданным экземпляром модели.

        Если был передан экземпляр не той же модели, что у `self`, вернется False в любом случае.

        Args:
            item (Base): объект, с которым будет сравниваться self.
            *as_dict_args (str): поля модели.
            **as_dict_kwargs (str): поля модели для замены.

        Returns:
            bool: является ли сравниваемый объект сходим с другим объектом модели.
        """
        if type(item) != type(self):  # type: ignore
            return False
        # TODO: заменить на полную проверку по всем колонкам модели.
        item_dict = item.as_dict(*as_dict_args, **as_dict_kwargs)
        self_dict = self.as_dict(*as_dict_args, **as_dict_kwargs)
        for field, value in item_dict.items():
            self_field_value = self_dict[field]
            if self_field_value != value:
                return True
        return False

    def is_different_from(
        self,
        item: Union[dict[str, Any], BaseModel, 'Base'],
        # TODO: переделать без *args, **kwargs
        *as_dict_args: str,
        **as_dict_kwargs: str,
    ) -> bool:
        """Проверка экземпляра модели на соответствие с переданными данными.

        Args:
            item (dict[str, Any] | BaseModel | Base): объект, с которым будет сравниваться self.
            *as_dict_args (str): поля модели.
            **as_dict_kwargs (str): поля модели для замены.

        Raises:
            TypeError: выбрасывается, когда был передан невалидный тип аргумента `item`.

        Returns:
            bool: является ли сравниваемый объект сходим с искомым.
        """
        if isinstance(item, BaseModel):
            return self._is_pydantic_different_from(item)
        if isinstance(item, self.__class__):
            return self._is_model_different_from(item, *as_dict_args, **as_dict_kwargs)
        if isinstance(item, dict):  # type: ignore
            return self._is_dict_different_from(item)
        raise TypeError(
            'Был передан item неправильного типа данных. Ожидались: Dict, BaseModel, Base. '
            f'Пришёл: {type(item)}.',
        )
