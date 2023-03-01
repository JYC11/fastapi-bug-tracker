# model data generation here
# take the dicts from the conftest in the main test folder and use them for making models
from uuid import UUID

import pytest_asyncio
from argon2 import PasswordHasher

from app.service.bugs import commands as bug_commands
from app.service.bugs import handlers as bug_handlers
from app.service.unit_of_work import AbstractUnitOfWork
from app.service.users import commands as user_commands
from app.service.users import handlers as user_handlers


@pytest_asyncio.fixture
async def create_user_id(
    uow: AbstractUnitOfWork,
    user_data_in: dict,
    password_hasher: PasswordHasher,
) -> UUID:
    cmd = user_commands.CreateUser(**user_data_in)
    user_id = await user_handlers.create_user(cmd, uow=uow, hasher=password_hasher)
    assert user_id
    return user_id


@pytest_asyncio.fixture
async def create_bug_id(
    uow: AbstractUnitOfWork,
    create_user_id: UUID,
    bug_data_in: dict,
) -> tuple[UUID, UUID]:
    bug_data_in["author_id"] = create_user_id
    bug_data_in["assignee_id"] = None
    cmd = bug_commands.CreateBug(**bug_data_in)
    bug_id = await bug_handlers.create_bug(cmd, uow=uow)
    assert bug_id
    return bug_id, create_user_id
