from sqlalchemy import Column, ColumnElement, Integer, MetaData, Table, false

from app.utils import operators as operator_utils


def test_do_nothing() -> None:
    """Проверка ничегонеделанья."""
    assert operator_utils.do_nothing() is None


def test_return_same_value() -> None:
    """Проверка возврата того же ответа."""
    assert operator_utils.return_value(25) == 25


def test_between() -> None:
    """Проверка значения между двумя другими: python mode."""
    assert operator_utils.between(25, (12, 26), sqlalchemy_mode=False) is True
    assert operator_utils.between(25, (2, 12), sqlalchemy_mode=False) is False
    assert operator_utils.between(25, (2,), sqlalchemy_mode=False) is False  # type: ignore


def test_between_sqlalchemy() -> None:
    """Проверка значения между двумя другими: sqlalchemy mode."""
    metadata = MetaData()
    table = Table('test_table_1', metadata, Column('id', Integer))
    assert isinstance(
        operator_utils.between(table.columns['id'], (12, 26), sqlalchemy_mode=True),
        ColumnElement,
    )
    assert (
        operator_utils.between(table.columns['id'], (12,), sqlalchemy_mode=True)  # type: ignore
        is false()
    )


def test_contains() -> None:
    """Проверка вхождения значения в последовательность: python mode."""
    assert operator_utils.contains(25, [1, 2, 3, 4, 5, 25], sqlalchemy_mode=False) is True
    assert operator_utils.contains(25, [1, 2, 3, 4, 5], sqlalchemy_mode=False) is False


def test_contains_sqlalchemy() -> None:
    """Проверка вхождения значения в последовательность: python mode."""
    metadata = MetaData()
    table = Table('test_table_1', metadata, Column('id', Integer))
    assert isinstance(
        operator_utils.contains(table.columns['id'], [1, 2, 3, 4], sqlalchemy_mode=True),
        ColumnElement,
    )
