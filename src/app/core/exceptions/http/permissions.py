from .base import BaseVerboseHTTPException


class BasePermissionError(BaseVerboseHTTPException):
    """Базовая ошибка доступа к ресурсу."""

    code = 'permission_denied'
    type_ = 'authentication_error'
    message = 'Отказ в доступе к ресурсу.'


class NoOneAllowedError(BasePermissionError):
    """Исключение ошибки доступа любого пользователя к ресурсу."""

    code = 'any_permission_denied'
    message = 'Ресурс недоступен ни для одного из пользователей.'


class AnonNotAllowedError(BasePermissionError):
    """Исключение ошибки доступа анонимного пользователя к ресурсу."""

    code = 'anon_permission_denied'
    message = 'Анонимный пользователь не имеет доступ к данному ресурсу.'


class UserNotAllowedError(BasePermissionError):
    """Исключение ошибки доступа пользователя к ресурсу."""

    code = 'user_permission_denied'
    message = 'Пользователь не имеет доступ к данному ресурсу.'


class AdminNotAllowedError(BasePermissionError):
    """Исключение ошибки доступа администратора к ресурсу."""

    code = 'admin_permission_denied'
    message = 'Администратор не имеет доступ к данному ресурсу.'
