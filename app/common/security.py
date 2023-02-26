from datetime import datetime
from typing import Any
from uuid import uuid4

from jose import ExpiredSignatureError, jwt

from app.common import exceptions as exc
from app.common.settings import settings


def create_jwt_token(
    subject: str,
    private_claims: dict[str, Any] | None,
    refresh: bool,
):
    expiration_delta = (
        settings.jwt_settings.refresh_expiration_delta if refresh else settings.jwt_settings.expiration_delta
    )
    expiration_datetime = datetime.utcnow() + expiration_delta
    registered_claims = {"exp": expiration_datetime, "sub": subject, "iat": datetime.utcnow(), "jti": uuid4().hex}
    claims = registered_claims | private_claims if private_claims else registered_claims
    jwt_token = jwt.encode(
        claims=claims,
        key=settings.jwt_settings.secret_key.get_secret_value(),
        algorithm=settings.jwt_settings.algorithm,
    )
    return jwt_token


def validate_jwt_token(token: str):
    try:
        return jwt.decode(token=token, key=settings.jwt_settings.secret_key.get_secret_value())
    except ExpiredSignatureError:
        raise exc.TokenExpired("token has expired")
    except Exception as e:
        raise exc.InvalidToken(f"token is invalid: {str(e)}")
