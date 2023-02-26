import pytest
from argon2 import PasswordHasher
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.domain import enums
from app.domain.models import Users
from app.service.users.repository import UserRepository


@pytest.mark.asyncio
async def test_user_repository_create(
    session: AsyncSession,
    user_data_in: dict,
    password_hasher: PasswordHasher,
):
    user_repo = UserRepository(session=session)
    new_user = Users.create_user(user_data_in, password_hasher)
    user_repo.add(new_user)
    await session.commit()

    query = await session.execute(select(Users))
    user: Users | None = query.scalars().first()
    assert user is not None
    assert user.id == new_user.id


@pytest.mark.asyncio
async def test_user_repository_update(
    session: AsyncSession,
    user_data_in: dict,
    password_hasher: PasswordHasher,
):
    user_repo = UserRepository(session=session)
    new_user = Users.create_user(user_data_in, password_hasher)
    user_repo.add(new_user)
    await session.commit()

    update_data = {"user_type": enums.UserTypeEnum.PM, "is_admin": True}
    new_user.update_user(update_data, password_hasher)
    await session.commit()
    query = await session.execute(select(Users))
    user: Users | None = query.scalars().first()
    assert user is not None
    assert getattr(user, "user_type") == enums.UserTypeEnum.PM
    assert getattr(user, "is_admin") is True
    assert len(user.events) == 2

    new_user.delete_user()
    await session.commit()
    query = await session.execute(select(Users))
    del_user: Users | None = query.scalars().first()
    assert del_user is not None
    assert getattr(del_user, "user_status") == enums.RecordStatusEnum.DELETED
    assert len(user.events) == 3


@pytest.mark.asyncio
async def test_user_repository_delete(
    session: AsyncSession,
    user_data_in: dict,
    password_hasher: PasswordHasher,
):
    user_repo = UserRepository(session=session)
    new_user = Users.create_user(user_data_in, password_hasher)
    user_repo.add(new_user)
    await session.commit()

    await user_repo.remove(new_user.id)
    await session.commit()

    query = await session.execute(select(Users))
    user: Users | None = query.scalars().first()
    assert user is None
