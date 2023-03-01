from uuid import UUID

from argon2 import PasswordHasher
from sqlalchemy.future import select

from app.common import exceptions as common_exc
from app.common.security import create_jwt_token, validate_jwt_token
from app.domain import enums
from app.domain.models import Users
from app.domain.read_models import UserReadModel
from app.service import exceptions as exc
from app.service.unit_of_work import AbstractUnitOfWork
from app.service.users import commands, events


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
            refresh=True,
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

        id = UUID(decoded.sub) if isinstance(decoded.sub, str) else decoded.sub
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


async def create_user(cmd: commands.CreateUser, *, uow: AbstractUnitOfWork, hasher: PasswordHasher):
    async with uow:
        users: list[Users] = await uow.users.list(
            filters={
                "email__eq": cmd.email,
                "user_status__eq": enums.RecordStatusEnum.ACTIVE,
            }
        )
        if users:
            raise exc.DuplicateRecord(f"user with email {cmd.email} exists")
        data_in = cmd.dict()
        new_user = Users.create_user(data=data_in, hasher=hasher)
        uow.users.add(new_user)
        uow.event_store.add(new_user.generate_event_store())
        await uow.commit()
        _id = new_user.id
        return _id


async def update_user(cmd: commands.UpdateUser, *, uow: AbstractUnitOfWork, hasher: PasswordHasher):
    async with uow:
        user: Users | None = await uow.users.get(cmd.id)
        if not user:
            raise exc.ItemNotFound(f"user with id {cmd.id} not found")
        if not user.is_active:
            raise exc.ItemNotFound("user is deleted")
        data = cmd.dict(exclude_unset=True, exclude_none=True)
        user.update_user(data, hasher)
        uow.users.seen.add(user)
        uow.event_store.add(user.generate_event_store())
        await uow.commit()
        _id = user.id
        return _id


async def soft_delete_user(cmd: commands.SoftDeleteUser, *, uow: AbstractUnitOfWork):
    async with uow:
        user: Users | None = await uow.users.get(cmd.id)
        if not user:
            raise exc.ItemNotFound(f"user with id {cmd.id} not found")
        if not user.is_active:
            return
        user.delete_user()
        uow.users.seen.add(user)
        uow.event_store.add(user.generate_event_store())
        await uow.commit()
        return


# event handlers
async def insert_into_user_read_model(
    event: events.UserCreated,
    *,
    uow: AbstractUnitOfWork,
):
    async with uow:
        new_row = UserReadModel(
            id=event.id,
            username=event.username,
            email=event.email,
            user_type=event.user_type,
            user_status=event.user_status,
            is_admin=event.is_admin,
        )
        uow.session.add(new_row)
        await uow.commit()


async def update_user_read_model(
    event: events.UserUpdated,
    *,
    uow: AbstractUnitOfWork,
):
    async with uow:
        query = select(UserReadModel).where(UserReadModel.id == event.id)
        execution = await uow.session.execute(query)
        row: UserReadModel | None = execution.scalars().first()
        if row:
            for key in event.__dict__.keys():
                val = getattr(event, key)
                if val is not None:
                    setattr(row, key, val)
            await uow.commit()


async def soft_delete_user_read_model(
    event: events.UserSoftDeleted,
    *,
    uow: AbstractUnitOfWork,
):
    async with uow:
        query = select(UserReadModel).where(UserReadModel.id == event.id)
        execution = await uow.session.execute(query)
        row: UserReadModel | None = execution.scalars().first()
        if row:
            row.user_status = event.user_status
            await uow.commit()
