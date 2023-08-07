"""Модуль авторизации администратора в sqladmin."""
from typing import Self

from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request
from starlette.responses import RedirectResponse

from app.core.config import get_admin_settings
from app.core.exceptions.results import Err
from app.core.meta import Session
from app.db.repositories.admins import AdminRepository
from app.services import auth

admin_settings = get_admin_settings()


class AdminAuthBackend(AuthenticationBackend):
    """Backend для авторизации администратора в админ-панели."""

    async def login(self: Self, request: Request) -> bool:
        """Метод входа администратора в админ-панель."""
        form = await request.form()
        username, password = form["username"], form["password"]
        if not isinstance(username, str) or not isinstance(password, str):
            return False
        async with Session() as session:
            repo = AdminRepository(session)
            admin = await repo.get_by_username(username=username, ignore_permissions=True)
        if not admin:
            return False
        if password != admin.password:
            return False
        # доступ только по refresh-токену.
        token = auth.encode_jwt_token(admin.id, is_admin=True, is_refresh_token=True)
        request.session.update({"token": token})

        return True

    async def logout(self: Self, request: Request) -> bool:
        """Метод выхода администратора из админ-панели."""
        request.session.clear()
        return True

    async def authenticate(self: Self, request: Request) -> RedirectResponse | None:
        """Метод проверки токена администратора для предоставления доступа к админ-панели."""
        token = request.session.get("token")

        if not token:
            return RedirectResponse(request.url_for("admin:login"), status_code=302)

        result = auth.decode_jwt_token(token, is_refresh_token=True)
        if isinstance(result, Err):
            # TODO: сделать что-то для того, чтобы было понятно, что это ошибка токена
            return RedirectResponse(request.url_for("admin:login"), status_code=302)
        decoded = result.unwrap()
        if 'user_id' not in decoded:
            # TODO: сделать что-то для того, чтобы было понятно, что это ошибка токена
            return RedirectResponse(request.url_for("admin:login"), status_code=302)
        async with Session() as session:
            repo = AdminRepository(session)
            admin = await repo.get(item_identity=decoded['user_id'], ignore_permissions=True)
        if not admin:
            # TODO: сделать что-то для того, чтобы было понятно, что это ошибка токена
            return RedirectResponse(request.url_for("admin:login"), status_code=302)
        new_token = auth.encode_jwt_token(admin.id, is_admin=True, is_refresh_token=True)
        request.session.update({"token": new_token})


authentication_backend = AdminAuthBackend(secret_key=admin_settings.secret_key.get_secret_value())
