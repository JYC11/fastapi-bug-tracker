from uuid import UUID

from fastapi import APIRouter, Body, Depends, HTTPException, Path
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.entrypoints import dependencies as deps
from app.service import exceptions as service_exc
from app.service.messagebus import MessageBus
from app.service.users import commands, dto

router = APIRouter()


@router.post(
    "/login",
    response_model=dto.LoginSuccess,
    status_code=status.HTTP_200_OK,
)
async def login(
    messagebus: MessageBus = Depends(deps.get_message_bus),
    req: OAuth2PasswordRequestForm = Depends(),
):
    try:
        cmd = commands.Login(
            email=req.username,
            password=req.password,
        )
        res = await messagebus.handle(message=cmd)
        return res
    except service_exc.Unauthorized as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )
    except service_exc.ItemNotFound as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.post(
    "/refresh",
    response_model=dto.RefreshSuccess,
    status_code=status.HTTP_200_OK,
)
async def refresh(
    messagebus: MessageBus = Depends(deps.get_message_bus),
    req: dto.RefreshRequest = Body(...),
):
    try:
        cmd = commands.Refresh(
            grant_type=req.grant_type,
            refresh_token=req.refresh_token,
        )
        res = await messagebus.handle(message=cmd)
        return res
    except service_exc.Forbidden as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )


@router.post(
    "/user",
    status_code=status.HTTP_201_CREATED,
)
async def create_user(
    messagebus: MessageBus = Depends(deps.get_message_bus),
    req: dto.UserCreateIn = Body(...),
):
    try:
        cmd = commands.CreateUser(**req.dict())
        await messagebus.handle(message=cmd)
    except service_exc.DuplicateRecord as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        )


@router.put(
    "/user/{user_id}",
    status_code=status.HTTP_200_OK,
)
async def update_user(
    token: dict = Depends(deps.decode_token),
    messagebus: MessageBus = Depends(deps.get_message_bus),
    user_id: UUID = Path(..., title="user_id"),
    req: dto.UserUpdateIn = Body(...),
):
    try:
        cmd = commands.UpdateUser(id=user_id, **req.dict())
        await messagebus.handle(message=cmd)
    except service_exc.ItemNotFound as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.delete(
    "/user/{user_id}",
    status_code=status.HTTP_200_OK,
)
async def delete_user(
    token: dict = Depends(deps.decode_token),
    messagebus: MessageBus = Depends(deps.get_message_bus),
    user_id: UUID = Path(..., title="user_id"),
):
    try:
        cmd = commands.DeleteUser(id=user_id)
        await messagebus.handle(message=cmd)
    except service_exc.ItemNotFound as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.get("/user/{user_id}", status_code=status.HTTP_200_OK)
async def my_user_page(
    token: dict = Depends(deps.decode_token),
    session: AsyncSession = Depends(deps.get_reader_session),
):
    return "ok"


@router.get("/user/{user_id}/comments", status_code=status.HTTP_200_OK)
async def my_comments(
    token: dict = Depends(deps.decode_token),
    session: AsyncSession = Depends(deps.get_reader_session),
):
    return "ok"


@router.get("/user/{user_id}/bugs", status_code=status.HTTP_200_OK)
async def my_bugs(
    token: dict = Depends(deps.decode_token),
    session: AsyncSession = Depends(deps.get_reader_session),
):
    return "ok"
