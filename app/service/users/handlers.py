from uuid import uuid4

from argon2 import PasswordHasher

from app.domain import commands
from app.domain.models import Users
from app.service.unit_of_work import AbstractUnitOfWork


async def create_user(cmd: commands.CreateUser, *, uow: AbstractUnitOfWork, hasher: PasswordHasher):
    async with uow:
        data_in = cmd.dict()
        data_in["id"] = uuid4()
        new_user = Users.create_user(data=data_in, hasher=hasher)
        uow.users.add(new_user)
        event_store = new_user.generate_event_store()
        if event_store:
            uow.event_store.add(event_store)
        await uow.commit()
        return new_user


async def update_user(cmd: commands.UpdateUser, *, uow: AbstractUnitOfWork):
    async with uow:
        return


async def delete_user(cmd: commands.DeleteUser, *, uow: AbstractUnitOfWork):
    async with uow:
        return
