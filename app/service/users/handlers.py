from uuid import UUID, uuid4

from argon2 import PasswordHasher

from app.common import exceptions as common_exc
from app.common.security import create_jwt_token, validate_jwt_token
from app.domain import enums
from app.domain.models import Users
from app.service import exceptions as exc
from app.service.unit_of_work import AbstractUnitOfWork
from app.service.users import commands


async def create_user(cmd: commands.CreateUser, *, uow: AbstractUnitOfWork, hasher: PasswordHasher):
    async with uow:
        users: list[Users] = await uow.users.list(filters={"email__eq": cmd.email})
        if users:
            raise exc.DuplicateRecord(f"user with email {cmd.email} exists")
        data_in = cmd.dict()
        data_in["id"] = uuid4()
        new_user = Users.create_user(data=data_in, hasher=hasher)
        uow.users.add(new_user)
        uow.event_store.add(new_user.generate_event_store())
        await uow.commit()
        return new_user


async def update_user(cmd: commands.UpdateUser, *, uow: AbstractUnitOfWork, hasher: PasswordHasher):
    async with uow:
        user: Users | None = await uow.users.get(cmd.id)
        if not user:
            raise exc.ItemNotFound(f"user with id {cmd.id} not found")
        data = cmd.dict(exclude_unset=True, exclude_none=True)
        user.update_user(data, hasher)
        uow.event_store.add(user.generate_event_store())
        uow.commit()
        await uow.refresh(user)
        return user


async def delete_user(cmd: commands.DeleteUser, *, uow: AbstractUnitOfWork):
    async with uow:
        user: Users | None = await uow.users.get(cmd.id)
        if not user:
            raise exc.ItemNotFound(f"user with id {cmd.id} not found")
        user.delete_user()
        uow.event_store.add(user.generate_event_store())
        uow.commit()
        return


async def login(cmd: commands.Login, *, uow: AbstractUnitOfWork, hasher: PasswordHasher):
    async with uow:
        users: list[Users] = await uow.users.list(filters={"email__eq": cmd.email})
        if not users:
            raise exc.Unauthorized("email or password is incorrect")

        user: Users = users[0]
        if not user.verify_password(cmd.password, hasher):
            raise exc.Unauthorized("email or password is incorrect")

        if user.user_status == enums.RecordStatusEnum.DELETED:
            raise exc.ItemNotFound("user is deleted")
        if hasher.check_needs_rehash(user.password):
            user.set_password(cmd.password, hasher)

        private_claims = {
            "email": user.email,
            "user_type": user.user_type,
            "admin": user.is_admin,
        }
        token = create_jwt_token(
            subject=str(user.id),
            private_claims=private_claims,
            refresh=False,
        )
        refresh_token = create_jwt_token(
            subject=str(user.id),
            private_claims={"user_type": user.user_type},
            refresh=False,
        )
        return {
            "message": "logged in",
            "token": token,
            "refresh_token": refresh_token,
        }


async def refresh(cmd: commands.Refresh, *, uow: AbstractUnitOfWork):
    async with uow:
        if cmd.grant_type != "refresh_token":
            raise exc.Forbidden("incorrect grant type")
        try:
            decoded = validate_jwt_token(token=cmd.refresh_token)
        except common_exc.TokenExpired as e:
            raise exc.Forbidden(f"{str(e)}")
        except common_exc.InvalidToken as e:
            raise exc.Forbidden(f"{str(e)}")

        id = UUID(decoded["sub"]) if isinstance(decoded["sub"], str) else decoded["sub"]
        user: Users | None = await uow.users.get(id)
        if not user:
            raise exc.Forbidden("user not found")
        private_claims = {
            "email": user.email,
            "user_type": user.user_type,
            "admin": user.is_admin,
        }
        token = create_jwt_token(
            subject=str(user.id),
            private_claims=private_claims,
            refresh=False,
        )
        return {
            "message": "success",
            "token": token,
        }
