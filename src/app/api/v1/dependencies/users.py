from typing import TYPE_CHECKING

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from vetapp.schemas.jwt import bearer_scheme
from vetapp.services.jwt import get_user_id_from_access_token

from app.api.v1.dependencies.databases import get_repository
from app.db import repositories

user_repository_getter = get_repository(repositories.UsersRepository)
token_repository_getter = get_repository(repositories.TokenRepository)

if TYPE_CHECKING:
    from app.core.models.tables.users import User


http_unauthorized = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail='Неверные данные для входа',
    headers={'WWW-Authenticate': 'Bearer'},
)

http_forbidden = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail='Доступ запрещён. Неактивный аккаунт.',
)

http_user_admin_panel_permission_denied = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail='Доступ запрещён. Пользователь не может иметь доступ к админ-панели.',
)

http_admin_mobile_application_permission_denied = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail='Доступ запрещён. Администратор не может иметь доступ к мобильному приложению.',
)


def get_current_user(
    token: HTTPBearer = Depends(bearer_scheme),
    users_repo: repositories.UsersRepository = Depends(user_repository_getter),
    admin_repo: repositories.AdminRepository = Depends(admin_repository_getter),
    token_repo: repositories.TokenRepository = Depends(token_repository_getter),
) -> Optional[Union[models.User, models.Admin]]:
    """Выдает текущего пользователя по JWT-токену."""
    user = None
    if token_repo.is_token_logout(token=token.credentials):
        raise http_unauthorized
    is_admin, user_id = get_user_id_from_access_token(token.credentials)
    if not user_id:
        raise http_unauthorized
    if is_admin:
        user = admin_repo.get_admin_by_id(admin_id=user_id)
    else:
        user = users_repo.get_user_by_id(user_id=user_id)
    if not user:
        raise http_unauthorized
    return user


def get_current_active_user(
    current_user: Optional[Union[models.User, models.Admin]] = Depends(get_current_user),
) -> models.User:
    """Выдает текущего активного пользователя."""
    if not current_user:
        raise http_unauthorized
    if isinstance(current_user, models.Admin):
        raise http_admin_mobile_application_permission_denied
    if isinstance(current_user, models.User) and not current_user.is_active:
        raise http_forbidden
    return current_user


def get_current_active_admin(
    current_user: Optional[Union[models.User, models.Admin]] = Depends(get_current_user),
) -> models.Admin:
    """Выдает текущего активного администратора."""
    if not current_user:
        raise http_unauthorized
    if isinstance(current_user, models.User):
        raise http_user_admin_panel_permission_denied
    if isinstance(current_user, models.Admin) and current_user.disabled:
        raise http_forbidden
    return current_user
