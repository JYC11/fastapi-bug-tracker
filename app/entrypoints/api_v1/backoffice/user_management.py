from uuid import UUID

from fastapi import APIRouter, Depends, Path
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.domain.common_schemas import Token
from app.entrypoints import dependencies as deps

router = APIRouter()


@router.get("/users", status_code=status.HTTP_200_OK)
async def get_users(
    token: Token = Depends(deps.decode_token),
    session: AsyncSession = Depends(deps.get_reader_session),
):
    return


@router.get("/user/{user_id}", status_code=status.HTTP_200_OK)
async def get_user(
    token: Token = Depends(deps.decode_token),
    session: AsyncSession = Depends(deps.get_reader_session),
    user_id: UUID = Path(..., title="user_id"),
):
    return
