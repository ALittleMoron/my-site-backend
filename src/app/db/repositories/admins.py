from typing import Self

from app.core.models.tables.admins import Admin
from app.db.mixins.permissions import PermissionModeEnum
from app.db.queries.base import BaseQuery
from app.db.repositories.base import BaseRepository


class AdminRepository(BaseRepository[Admin, BaseQuery]):
    """Репозиторий для работы c администратором."""

    async def get_by_username(
        self: Self,
        *,
        username: str,
        permission_mode: PermissionModeEnum = PermissionModeEnum.ANYONE,
        ignore_permissions: bool = False,
    ) -> Admin | None:
        """Отдает администратора по его уникальному имени (username)."""
        result = await super().get(
            item_identity=username,
            item_identity_field='username',
            permission_mode=permission_mode,
            ignore_permissions=ignore_permissions,
        )
        return result
