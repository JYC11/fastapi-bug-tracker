from uuid import UUID

from argon2 import PasswordHasher
from fastapi import Depends, HTTPException, Path
from fastapi.security import OAuth2PasswordBearer
from jose import ExpiredSignatureError
from starlette import status

from app.common.db import async_autocommit_session_factory
from app.common.security import validate_jwt_token
from app.common.settings import settings
from app.service.messagebus import MessageBus, MessageBusFactory
from app.service.unit_of_work import SqlAlchemyUnitOfWork

MESSAGEBUS = MessageBusFactory(
    uow=SqlAlchemyUnitOfWork(),
    password_hasher=PasswordHasher(),
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=settings.api_v1_login_url)


def get_message_bus() -> MessageBus:
    return MESSAGEBUS()


def get_reader_session():
    assert async_autocommit_session_factory is not None
    with async_autocommit_session_factory() as session:
        yield session


async def decode_token(
    token: str = Depends(oauth2_scheme),
    user_id: UUID | None = Path(...),
):
    try:
        decoded_token = validate_jwt_token(token)
        if str(user_id) != decoded_token.sub:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="token and user_id mismatch")
        return decoded_token
    except ExpiredSignatureError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
