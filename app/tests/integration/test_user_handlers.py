import pytest
from argon2 import PasswordHasher

from app.service.unit_of_work import AbstractUnitOfWork
from app.service.users import commands, handlers


@pytest.mark.asyncio
async def test_create_user_handler(
    uow: AbstractUnitOfWork,
    user_data_in: dict,
    password_hasher: PasswordHasher,
):
    cmd = commands.CreateUser(**user_data_in)
    user = await handlers.create_user(cmd, uow=uow, hasher=password_hasher)
    assert user
