from uuid import UUID

from argon2 import PasswordHasher
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import ExpiredSignatureError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from starlette import status

from app.common.db import async_autocommit_session_factory
from app.common.security import validate_jwt_token
from app.common.settings import settings
from app.domain.models import Users
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


async def decode_token(token: str = Depends(oauth2_scheme), session: AsyncSession = Depends(get_reader_session)):
    try:
        decoded_token = validate_jwt_token(token)
        query = await session.execute(select(Users).where(Users.id == UUID(decoded_token["sub"])))
        user: Users | None = query.scalars().first()
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="user does not exist")
        if not user.is_active():  # type: ignore
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="user is not active")
        return user
    except ExpiredSignatureError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
