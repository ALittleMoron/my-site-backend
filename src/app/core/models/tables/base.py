"""Модуль базовых таблиц моделей данных проекта."""
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel
from sqlalchemy import inspect
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.orm import DeclarativeBase

from app.core.config import get_logger

if TYPE_CHECKING:
    FieldSequence = set[str]
    OptionalFieldSequence = FieldSequence | None

logger = get_logger('app')
ATTR_NOT_FOUND_TEMPLATE = 'Атрибут "{field}" не был найден в модели {class_name}.'
NOT_LOADED_VALUE = '<Not loaded>'


class Base(DeclarativeBase):
    """Базовый класс для объявления моделей SQLAlchemy."""

    __abstract__ = True

    max_repr_elements: int | None = None
    differ_include_fields: 'OptionalFieldSequence' = None
    repr_include_fields: 'OptionalFieldSequence' = None
    default_include_fields: 'OptionalFieldSequence' = None
    default_replace_fields: dict[str, str] | None = None

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
            value = self._get_model_attr(variable_name)
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
            value_to_replace = self._get_model_attr(replaced)
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
            include = self.default_include_fields  # type: ignore
        self._add_by_includes(item, *include)
        if not replace and self.default_replace_fields is not None:
            replace = self.default_replace_fields
        self._replace(item, **replace)
        return item

    def _is_dict_different_from(
        self: 'Base',
        item: dict[str, Any],
        *include_fields: str,
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
        _include_fields = include_fields or self.differ_include_fields
        for field, value in item.items():
            if _include_fields and field not in _include_fields:
                continue
            if not hasattr(self, field):
                msg = ATTR_NOT_FOUND_TEMPLATE.format(
                    field=field,
                    class_name=self.__class__.__name__,
                )
                logger.warning('MODEL IS-DIFFERENT-FROM W1: %s', msg)
                return True
            self_field_value = getattr(self, field)
            if self_field_value != value:
                return True
        return False

    def _is_pydantic_different_from(
        self: 'Base',
        item: BaseModel,
        *include_fields: str,
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
        item_dict = item.model_dump(include=set(include_fields))
        return self._is_dict_different_from(item_dict, *include_fields)

    def _is_model_different_from(
        self: 'Base',
        item: 'Base',
        *include_fields: str,
    ) -> bool:
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
        item_dict = {col.name: getattr(item, col.name) for col in item.__table__.columns}
        self_dict = {col.name: getattr(self, col.name) for col in self.__table__.columns}
        _include_fields = include_fields or self.differ_include_fields
        for field, value in item_dict.items():
            if _include_fields and field not in _include_fields:
                continue
            self_field_value = self_dict[field]
            if self_field_value != value:
                return True
        return False

    def is_different_from(
        self: 'Base',
        item: 'dict[str, Any] | BaseModel | Base',
        include_fields: set[str] | None = None,
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
        if not include_fields:
            include_fields = set()
        if isinstance(item, BaseModel):
            return self._is_pydantic_different_from(item, *include_fields)
        if isinstance(item, self.__class__):
            return self._is_model_different_from(item, *include_fields)
        if isinstance(item, dict):  # type: ignore
            return self._is_dict_different_from(item, *include_fields)
        msg = (
            'Был передан item неправильного типа данных. '
            f'Ожидались: Dict, BaseModel, {self.__class__.__name__}. Пришёл: {type(item)}.'
        )
        raise TypeError(msg)

    def __repr__(self: 'Base') -> str:
        """Строковая репрезентация экземпляра класса модели.

        Выводит всё наполнение модели, но только для колонок модели. Игнорирует гибридные и обычные
        свойства. Выводит только то, что реально хранится в базе данных (с поправкой на '
        'конвертацию данных в типы данных Python).
        """
        class_name = self.__class__.__name__
        try:
            inspector = inspect(self)
        except InvalidRequestError as exc:
            msg = (
                f'BASE-REPR W1: не получилось создать инспектора для модели "{class_name}". '
                f'Ошибка: {exc}'
            )
            logger.warning(msg)
            return f'{class_name}(<Not representable (inspect failed)>)'
        has_id_column = False
        fields = self.__table__.columns.keys()
        # (1) для того, чтобы id был всегда первым в итоговом repr, его сначала извлекаем...
        values_pairs_list: list[str] = []
        if 'id' in fields:
            has_id_column = True
            if 'id' not in inspector.unloaded:  # type: ignore
                id_column_repr = f'id={self.id}'  # type: ignore
            else:
                id_column_repr = f'id={NOT_LOADED_VALUE}'
            # (2) ..., затем добавляем в values_pairs_list как первое значение ...
            values_pairs_list.append(id_column_repr)
        for col in fields:
            # (3) ...и в итоге проверяем, чтобы id снова не был добавлен в итоговый список.
            if has_id_column and col == 'id':
                continue
            elif col in inspector.unloaded:  # type: ignore
                values_pairs_list.append(f'{col}={NOT_LOADED_VALUE}')
            elif not self.repr_include_fields or col in self.repr_include_fields:
                values_pairs_list.append(f'{col}={repr(getattr(self, col))}')
        if self.max_repr_elements:
            values_pairs_list = values_pairs_list[: self.max_repr_elements]
        values_pairs = ', '.join(values_pairs_list)
        return f'{class_name}({values_pairs})'
