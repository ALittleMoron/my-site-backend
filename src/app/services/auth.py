import datetime
from typing import Any
from uuid import UUID

import jwt
from passlib import context

from app.core.config import get_auth_settings, get_logger
from app.core.exceptions.results import Err, Ok, Result
from app.utils.datetime import get_utc_now

logger = get_logger('app')
IsAdmin = bool
AccessToken = bytes
RefreshToken = bytes

settings = get_auth_settings()
pwd_context = context.CryptContext(schemes=settings.hasher_schema, deprecated='auto')


def verify_password(plain_password: str | bytes, hashed_password: str | bytes) -> bool:
    """Проверяет пароль и хэш пароля на соответствие."""
    return pwd_context.verify(plain_password, hashed_password)


def generate_password_hash(password: str | bytes) -> str:
    """Генерирует hash для пароля."""
    return pwd_context.hash(password)


def encode_jwt_token(
    user_id: int | UUID | str,
    *,
    is_admin: bool = False,
    is_refresh_token: bool = False,
) -> AccessToken | RefreshToken:
    """Создание JWT-токена."""
    if isinstance(user_id, UUID):
        user_id = str(user_id)
    key = settings.refresh_secret_key if is_refresh_token else settings.access_secret_key
    expire_time_delta_seconds = (
        settings.refresh_expire_time if is_refresh_token else settings.access_expire_time
    )
    expire_time_delta = datetime.timedelta(seconds=expire_time_delta_seconds)
    payload = {
        'user_id': user_id,
        'is_admin': is_admin,
        'exp': get_utc_now() + expire_time_delta,
    }
    return jwt.encode(
        payload=payload,
        key=key.get_secret_value(),
        algorithm=settings.hasher_algorithm,
    )


def encode_jwt_tokens_pair(
    user_id: int,
    *,
    is_admin: bool = False,
) -> tuple[AccessToken, RefreshToken]:
    """Создаете пару access + refresh."""
    access_token = encode_jwt_token(user_id, is_admin=is_admin)
    refresh_token = encode_jwt_token(user_id, is_admin=is_admin, is_refresh_token=True)
    return access_token, refresh_token


def decode_jwt_token(
    token: str | bytes,
    *,
    is_refresh_token: bool = False,
) -> Result[dict[str, Any], jwt.PyJWTError]:
    """Преобразование JWT-токена в словарь."""
    key = settings.refresh_secret_key if is_refresh_token else settings.access_secret_key
    decoded_token: dict[str, Any] = {}
    try:
        decoded_token = jwt.decode(
            jwt=token,
            key=key.get_secret_value(),
            algorithms=settings.hasher_algorithm,
        )
        result = Ok(decoded_token)
    except jwt.ExpiredSignatureError as exc:
        logger.warning('TOKEN-DECODE E1: Время жизни токена "%s" исчерпано.', token)
        result = Err(exc)
    except jwt.PyJWTError as exc:
        logger.exception('TOKEN-DECODE E2: отловлена базовая ошибка PyJWT.')
        result = Err(exc)
    return result  # type: ignore
