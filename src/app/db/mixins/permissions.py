import enum
from typing import TYPE_CHECKING, Literal

from app.core.config import get_logger
from app.core.exceptions.http import permissions as permission_http_exceptions
from app.core.exceptions.results import Err

if TYPE_CHECKING:
    from sqlalchemy.sql.elements import ColumnElement

    PermissionMethodNames = (
        Literal['create']
        | Literal['read_list']
        | Literal['read_count']
        | Literal['read_detail']
        | Literal['update']
        | Literal['disable']
        | Literal['delete']
    )
    JoinRequired = bool


logger = get_logger('app')


class PermissionModeEnum(int, enum.Enum):
    """Enum режимов получения данных вместе со связанными сущностями.

    Определяет то, будут ли произведены join'ы и options, или нет.
    """

    ANYONE = enum.auto()
    ANON = enum.auto()
    USER = enum.auto()
    ADMIN = enum.auto()
    NO_ONE = enum.auto()


class PermissionMixin:
    """Примесь контроля доступа."""

    PERMISSION_RULES: 'dict[PermissionMethodNames, PermissionModeEnum]' = {
        'create': PermissionModeEnum.ANYONE,
        'read_list': PermissionModeEnum.ANYONE,
        'read_count': PermissionModeEnum.ANYONE,
        'read_detail': PermissionModeEnum.ANYONE,
        'update': PermissionModeEnum.ANYONE,
        'delete': PermissionModeEnum.ANYONE,
        'disable': PermissionModeEnum.ANYONE,
    }

    @property
    def anon_visibility_filters(
        self: 'PermissionMixin',
    ) -> 'tuple[JoinRequired, tuple[ColumnElement[bool], ...]]':
        """Выдает фильтры для контроля видимости сущностей неавторизованным пользователем."""
        raise NotImplementedError()

    @property
    def user_visibility_filters(
        self: 'PermissionMixin',
    ) -> 'tuple[JoinRequired, tuple[ColumnElement[bool], ...]]':
        """Выдает фильтры для контроля видимости сущностей пользователем."""
        raise NotImplementedError()

    @property
    def admin_visibility_filters(
        self: 'PermissionMixin',
    ) -> 'tuple[JoinRequired, tuple[ColumnElement[bool], ...]]':
        """Выдает фильтры для контроля видимости сущностей администратором."""
        raise NotImplementedError()

    def check_permissions(
        self: 'PermissionMixin',
        method_name: 'PermissionMethodNames',
        mode: 'PermissionModeEnum',
        *,
        ignore_permissions: bool = False,
        ignore_method_name: str = '<not known>',
    ) -> None:
        """Метод проверки переданного режима доступа и разрешенного для выбранного метода."""
        log_prefix = 'CHECK-PERMISSION'
        if ignore_permissions:
            msg = f'игнорирование при проверке доступа к методу "{ignore_method_name}".'
            logger.warning('%s W1: %s', log_prefix, msg)
            return
        if method_name not in self.PERMISSION_RULES:
            msg = (
                f'отказ в доступе (нет правила "{method_name}" для проверки). '
                f'Метод: {ignore_method_name}'
            )
            logger.error('%s E1: %s', log_prefix, msg)
            Err(permission_http_exceptions.BasePermissionError()).unwrap()
        permitted_mode = self.PERMISSION_RULES[method_name]
        if mode.value >= permitted_mode.value:
            return None
        match mode:
            case PermissionModeEnum.ANON:
                result = Err(permission_http_exceptions.AnonNotAllowedError())
            case PermissionModeEnum.USER:
                result = Err(permission_http_exceptions.UserNotAllowedError())
            case PermissionModeEnum.ADMIN:
                result = Err(permission_http_exceptions.AdminNotAllowedError())
            case PermissionModeEnum.NO_ONE:
                result = Err(permission_http_exceptions.NoOneAllowedError())
            case _:
                return None
        msg = (
            f'отказ в доступе (уровень доступа "{mode}" выше, чем "{permitted_mode}"). '
            f'Метод "{ignore_method_name}"'
        )
        logger.error('%s E2: %s', log_prefix, msg)
        result.unwrap()

    def get_visibility_filter_from_permission(
        self: 'PermissionMixin',
        method_name: 'PermissionMethodNames',
        mode: PermissionModeEnum,
        *,
        ignore_permissions: bool = False,
        ignore_method_name: str = '<not known>',
    ) -> 'tuple[JoinRequired, tuple[ColumnElement[bool], ...]]':
        """Достает фильтры для контроля видимости по переданному режиму контроля."""
        self.check_permissions(
            method_name=method_name,
            mode=mode,
            ignore_permissions=ignore_permissions,
            ignore_method_name=ignore_method_name,
        )
        match mode:
            case PermissionModeEnum.ANON:
                return self.anon_visibility_filters
            case PermissionModeEnum.USER:
                return self.user_visibility_filters
            case PermissionModeEnum.ADMIN:
                return self.admin_visibility_filters
            case _:
                return (False, ())
