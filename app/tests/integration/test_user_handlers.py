from copy import deepcopy
from uuid import uuid4

import pytest
from argon2 import PasswordHasher

from app.common.security import create_jwt_token
from app.domain import enums
from app.domain.models import EventStore, Users
from app.service import exceptions as service_exc
from app.service.unit_of_work import AbstractUnitOfWork
from app.service.users import commands, handlers


@pytest.mark.asyncio
async def test_create_user_handler(
    uow: AbstractUnitOfWork,
    user_data_in: dict,
    password_hasher: PasswordHasher,
):
    cmd = commands.CreateUser(**user_data_in)
    user_id = await handlers.create_user(cmd, uow=uow, hasher=password_hasher)
    assert user_id
    async with uow:
        found_user: list[Users] = await uow.users.list()
        found_events: list[EventStore] = await uow.event_store.get(user_id)
        assert len(found_user) == 1
        assert user_id == found_user[0].id
        assert found_events, len(found_events) == 1
        assert user_id == found_events[0].aggregate_id
        assert found_events[0].event_name == "UserCreated"

    # unhappy path testcase
    try:
        await handlers.create_user(cmd, uow=uow, hasher=password_hasher)  # try again
    except service_exc.DuplicateRecord:
        assert True


@pytest.mark.asyncio
async def test_update_user_with_handlers(
    uow: AbstractUnitOfWork,
    user_data_in: dict,
    password_hasher: PasswordHasher,
):
    cmd = commands.CreateUser(**user_data_in)
    user_id = await handlers.create_user(cmd, uow=uow, hasher=password_hasher)
    update_data = deepcopy(user_data_in)
    update_data["username"] = "foobar"
    update_data["email"] = "foobar@gmail.com"

    update_cmd = commands.UpdateUser(id=user_id, **update_data)
    updated_user = await handlers.update_user(update_cmd, uow=uow, hasher=password_hasher)
    assert updated_user
    async with uow:
        found_user: list[Users] = await uow.users.list()
        found_events1: list[EventStore] = await uow.event_store.get(user_id)
        assert found_user[0].username == update_data["username"]
        assert found_user[0].email == update_data["email"]
        assert found_events1, len(found_events1) == 2
        assert found_events1[0].event_name == "UserCreated"
        assert found_events1[1].event_name == "UserUpdated"

    # in essence, the delete handler is just the update handler but specialised
    delete_cmd = commands.SoftDeleteUser(id=user_id)
    await handlers.soft_delete_user(delete_cmd, uow=uow)
    async with uow:
        deleted_user: list[Users] = await uow.users.list()
        found_events2: list[EventStore] = await uow.event_store.get(user_id)
        assert deleted_user[0].user_status == enums.RecordStatusEnum.DELETED
        assert found_events2, len(found_events2) == 3
        assert found_events2[0].event_name == "UserCreated"
        assert found_events2[1].event_name == "UserUpdated"
        assert found_events2[2].event_name == "UserSoftDeleted"

    # unhappy path: update handler not found test case
    update_cmd.id = uuid4()
    try:
        await handlers.update_user(update_cmd, uow=uow, hasher=password_hasher)
        assert False
    except service_exc.ItemNotFound:
        assert True

    # unhappy path: delete handler not found test case
    delete_cmd.id = uuid4()
    try:
        await handlers.soft_delete_user(delete_cmd, uow=uow)
        assert False
    except service_exc.ItemNotFound:
        assert True

    # unhappy path: user is deleted test case
    update_cmd.id = user_id
    try:
        await handlers.update_user(update_cmd, uow=uow, hasher=password_hasher)
        assert False
    except service_exc.ItemNotFound:
        assert True


@pytest.mark.asyncio
async def test_login_handler(
    uow: AbstractUnitOfWork,
    user_data_in: dict,
    password_hasher: PasswordHasher,
):
    email = user_data_in["email"]
    password = user_data_in["password"]
    cmd = commands.CreateUser(**user_data_in)
    user_id = await handlers.create_user(cmd, uow=uow, hasher=password_hasher)
    assert user_id

    try:
        ideal_login = commands.Login(email=email, password=password)
        tokens = await handlers.login(ideal_login, uow=uow, hasher=password_hasher)
        assert tokens["message"] == "logged in"
        assert tokens["token"] is not None
        assert tokens["refresh_token"] is not None
    except (service_exc.Unauthorized, service_exc.ItemNotFound):
        assert False

    # unhappy paths
    try:
        bad_email = commands.Login(email="email", password=password)
        await handlers.login(bad_email, uow=uow, hasher=password_hasher)
        assert False
    except service_exc.Unauthorized:
        assert True

    try:
        bad_password = commands.Login(email=email, password="password")
        await handlers.login(bad_password, uow=uow, hasher=password_hasher)
        assert False
    except service_exc.Unauthorized:
        assert True

    delete_cmd = commands.SoftDeleteUser(id=user_id)
    await handlers.soft_delete_user(delete_cmd, uow=uow)
    try:
        deleted = commands.Login(email=email, password=password)
        await handlers.login(deleted, uow=uow, hasher=password_hasher)
        assert False
    except service_exc.ItemNotFound:
        assert True


@pytest.mark.asyncio
async def test_refresh_handler(
    uow: AbstractUnitOfWork, user_data_in: dict, password_hasher: PasswordHasher, expired_refresh_token: str
):
    email = user_data_in["email"]
    password = user_data_in["password"]
    cmd = commands.CreateUser(**user_data_in)
    user_id = await handlers.create_user(cmd, uow=uow, hasher=password_hasher)
    assert user_id

    login = commands.Login(email=email, password=password)
    tokens = await handlers.login(login, uow=uow, hasher=password_hasher)

    try:
        good_refresh = commands.Refresh(
            refresh_token=tokens["refresh_token"],
            grant_type="refresh_token",
        )
        await handlers.refresh(good_refresh, uow=uow)
        assert True
    except service_exc.Forbidden:
        assert False

    # unhappy paths
    try:
        bad_grant = commands.Refresh(
            refresh_token=tokens["refresh_token"],
            grant_type="not refresh_token",
        )
        await handlers.refresh(bad_grant, uow=uow)
        assert False
    except service_exc.Forbidden:
        assert True

    try:
        invalid_token = commands.Refresh(
            refresh_token="invalid_token",
            grant_type="refresh_token",
        )
        await handlers.refresh(invalid_token, uow=uow)
        assert False
    except service_exc.Forbidden:
        assert True

    try:
        expired_token = commands.Refresh(
            refresh_token=expired_refresh_token,
            grant_type="refresh_token",
        )
        await handlers.refresh(expired_token, uow=uow)
        assert False
    except service_exc.Forbidden:
        assert True

    user_not_found_refresh_token = create_jwt_token(
        subject=str(uuid4()),
        private_claims={"user_type": "something cool"},
        refresh=True,
    )
    try:
        expired_token = commands.Refresh(
            refresh_token=user_not_found_refresh_token,
            grant_type="refresh_token",
        )
        await handlers.refresh(expired_token, uow=uow)
        assert False
    except service_exc.Forbidden:
        assert True
