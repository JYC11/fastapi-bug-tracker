# api data generation here
# take the dicts from the conftest in the main test folder and use them for api calls
from http import HTTPStatus

import httpx
from fastapi import FastAPI

from app.common.settings import settings


# if I want to just test with unauthenticated user
async def create_test_user(app: FastAPI, user_data_in: dict):
    create_url = app.url_path_for("create_user")
    async with httpx.AsyncClient(app=app, base_url=settings.test_url) as ac:
        await ac.post(create_url, json=user_data_in)
    return


async def test_user_login(app: FastAPI, username: str, password: str):
    login_data = {
        "username": username,
        "password": password,
    }

    login_url = app.url_path_for("login")
    async with httpx.AsyncClient(app=app, base_url=settings.test_url) as ac:
        logged_in_res = await ac.post(login_url, data=login_data)
    assert logged_in_res.status_code == HTTPStatus.OK
    return logged_in_res.json()


# if I want to just test with authenticated user
async def create_user_and_login(app: FastAPI, user_data_in: dict):
    await create_test_user(app=app, user_data_in=user_data_in)
    res = await test_user_login(
        app=app,
        username=user_data_in["email"],
        password=user_data_in["password"],
    )
    return {"Authorization": f"Bearer {res['token']}"}
