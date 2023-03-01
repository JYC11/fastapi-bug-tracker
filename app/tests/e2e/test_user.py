from http import HTTPStatus

import httpx
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.common.settings import settings
from app.domain.models import Users
from app.main import app
from app.tests.e2e.conftest import create_user_and_login


def test_health_check(client: TestClient):
    url = app.url_path_for("health")
    resp = client.get(url)
    resp_body = resp.json()
    assert resp.status_code == HTTPStatus.OK, resp_body
    assert resp_body == "ok"


@pytest.mark.asyncio
async def test_create_user(
    test_app: FastAPI,
    user_data_in: dict,
    session: AsyncSession,
):
    url = test_app.url_path_for("create_user")
    async with httpx.AsyncClient(app=test_app, base_url=settings.test_url) as ac:
        res = await ac.post(url, json=user_data_in)
    assert res.status_code == HTTPStatus.CREATED

    execution = await session.execute(select(Users))
    users = execution.scalars().all()
    assert len(users) == 1
    # TODO: unhappy path test cases


@pytest.mark.asyncio
async def test_login_and_refresh_user(
    test_app: FastAPI,
    user_data_in: dict,
    session: AsyncSession,
):
    create_url = test_app.url_path_for("create_user")
    async with httpx.AsyncClient(app=test_app, base_url=settings.test_url) as ac:
        await ac.post(create_url, json=user_data_in)

    login_data = {
        "username": user_data_in["email"],
        "password": user_data_in["password"],
    }

    login_url = test_app.url_path_for("login")
    async with httpx.AsyncClient(app=test_app, base_url=settings.test_url) as ac:
        logged_in_res = await ac.post(login_url, data=login_data)
    logged_in_data = logged_in_res.json()
    assert logged_in_res.status_code == HTTPStatus.OK
    assert logged_in_data["message"] == "logged in"
    assert logged_in_data["token"] is not None
    assert logged_in_data["refresh_token"] is not None

    refresh_data = {
        "grant_type": "refresh_token",
        "refresh_token": logged_in_data["refresh_token"],
    }
    refresh_url = test_app.url_path_for("refresh")
    async with httpx.AsyncClient(app=test_app, base_url=settings.test_url) as ac:
        refresh_res = await ac.post(refresh_url, json=refresh_data)
    refresh_res_data = refresh_res.json()
    assert refresh_res.status_code == HTTPStatus.OK
    assert refresh_res_data["message"] == "success"
    assert refresh_res_data["token"] is not None

    # TODO: unhappy path test cases


@pytest.mark.asyncio
async def test_update_user(
    test_app: FastAPI,
    user_data_in: dict,
    session: AsyncSession,
):
    enduser_headers = await create_user_and_login(
        app=test_app,
        user_data_in=user_data_in,
    )

    execution = await session.execute(select(Users))
    users: list[Users] = execution.scalars().all()
    user = users[0]
    user_data_in["id"] = str(user.id)
    user_data_in["username"] = "something else"

    update_url = test_app.url_path_for("update_user", user_id=str(user.id))
    async with httpx.AsyncClient(app=test_app, base_url=settings.test_url) as ac:
        res = await ac.put(
            update_url,
            headers=enduser_headers,
            json=user_data_in,
        )
    assert res.status_code == HTTPStatus.OK
    execution1 = await session.execute(select(Users))
    users1: list[Users] = execution1.scalars().all()
    assert users1
    found_user: Users = users1[0]
    assert found_user.username == "something else"
    # TODO: unhappy path test cases


@pytest.mark.asyncio
async def test_delete_user(
    test_app: FastAPI,
    user_data_in: dict,
    session: AsyncSession,
):
    enduser_headers = await create_user_and_login(
        app=test_app,
        user_data_in=user_data_in,
    )

    execution = await session.execute(select(Users))
    users: list[Users] = execution.scalars().all()
    user = users[0]

    delete_url = test_app.url_path_for("delete_user", user_id=str(user.id))
    async with httpx.AsyncClient(app=test_app, base_url=settings.test_url) as ac:
        res = await ac.delete(
            delete_url,
            headers=enduser_headers,
        )
    assert res.status_code == HTTPStatus.OK
    execution1 = await session.execute(select(Users))
    users1: list[Users] = execution1.scalars().all()
    assert users1
    found_user: Users = users1[0]
    assert found_user.user_status == "deleted"
    # TODO: unhappy path test cases
