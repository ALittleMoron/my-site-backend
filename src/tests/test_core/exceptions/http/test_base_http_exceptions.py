from string import Template

import pytest

from app.core.exceptions.http import base as base_http_exceptions

attr = 'attr'
test_http_exception1_dict = {
    'code': 'test',
    'type': 'Test',
    'message': 'test message: test',
    'attr': 'attr',
}


class TestHttpException1(base_http_exceptions.BaseVerboseHTTPException):  # noqa: D101
    __test__ = False

    code = 'test'
    type_ = 'Test'
    message = 'test message'
    template = Template('test message: $test')


class TestHttpException2(base_http_exceptions.BaseVerboseHTTPException):  # noqa: D101
    __test__ = False

    code = 'test'
    type_ = 'Test'
    message = 'test message'
    template = 'test message: {test}'


def test_from_template_method() -> None:
    """Проверка метода from_template."""
    with pytest.raises(TestHttpException1) as exc_info:
        raise TestHttpException1.from_template(test='test')
    assert isinstance(TestHttpException1.template, Template)
    assert (
        exc_info.value.message
        == TestHttpException1.template.safe_substitute(test='test')
        == 'test message: test'
    )


def test_from_template_string_method() -> None:
    """Проверка метода from_template со строковым шаблоном."""
    with pytest.raises(TestHttpException2) as exc_info:
        raise TestHttpException2.from_template(test='test')
    assert isinstance(TestHttpException2.template, str)
    assert (
        exc_info.value.message
        == TestHttpException2.template.format(test='test')
        == 'test message: test'
    )


def test_with_attr_method() -> None:
    """Проверка метода with_attr."""
    with pytest.raises(TestHttpException1) as exc_info:
        raise TestHttpException1.with_attr(attr)
    assert exc_info.value.attr == TestHttpException1.attr == attr


def test_class_methods_chain() -> None:
    """Проверка объединенного использования нескольких методов класса."""
    with pytest.raises(TestHttpException1) as exc_info:
        raise TestHttpException1.from_template(test='test').with_attr(attr)
    assert isinstance(TestHttpException1.template, Template)
    assert (
        exc_info.value.message
        == TestHttpException1.template.safe_substitute(test='test')
        == 'test message: test'
    )
    assert exc_info.value.attr == TestHttpException1.attr == attr


def test_class_as_dict() -> None:
    """Проверка конвертации исключения в словарь."""
    with pytest.raises(TestHttpException1) as exc_info:
        raise TestHttpException1.from_template(test='test').with_attr(attr)
    assert (
        exc_info.value.as_dict()
        == TestHttpException1.from_template(test='test').with_attr(attr).as_dict()
        == test_http_exception1_dict
    )


def test_class_as_dict_with_params() -> None:
    """Проверка конвертации исключения в словарь с дополнительными параметрами."""
    with pytest.raises(TestHttpException1) as exc_info:
        raise TestHttpException1
    assert (
        exc_info.value.as_dict()
        == TestHttpException1.as_dict(attr_name=attr, test='test')
        == test_http_exception1_dict
    )
