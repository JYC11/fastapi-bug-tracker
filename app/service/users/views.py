from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.domain import common_schemas, enums
from app.domain.models import Bugs, Comments, Users
from app.service import exceptions as exc
from app.service.users.dto import UserOut
from app.utils.helpers import set_pagination


async def get_my_user_page(session: AsyncSession, user_id: UUID):
    query = (
        select(Users)
        .options(selectinload(Users.comments))
        .options(selectinload(Users.raised_bugs))
        .options(selectinload(Users.assigned_bugs))
        .where(Users.id == user_id, Users.user_status == enums.RecordStatusEnum.ACTIVE)
    )
    execution = await session.execute(query)
    user = execution.scalar_one_or_none()
    if not user:
        raise exc.ItemNotFound(f"user with id {id} not found")
    return UserOut.from_orm(user)


async def get_my_comments(
    session: AsyncSession,
    user_id: UUID,
    search_query: dict | None,
    ordering: str | None,
    page: int | None,
    count_per_page: int | None,
):
    query = (
        select(Comments)
        .options(selectinload(Comments.bug))
        .options(selectinload(Comments.author))
        .where(Comments.author_id == user_id)
        .join(Bugs, Bugs.id == Comments.bug_id)
    )
    # TODO: add filters
    query = set_pagination(query, page, count_per_page)
    # TODO: set ordering
    execution = await session.execute(query)
    comments = execution.scalars().all()
    return comments


async def get_my_bugs(
    session: AsyncSession,
    user_id: UUID,
    search_query: dict | None,
    ordering: str | None,
    page: int | None,
    count_per_page: int | None,
):
    query = (
        select(Bugs)
        .options(selectinload(Bugs.comments))
        .options(selectinload(Bugs.author))
        .options(selectinload(Bugs.assignee))
    )
    # TODO: add more filters
    filters = []
    if search_query:
        for key, value in search_query.items():
            _like_search = f"%{value}%"
            if key == "author":
                filters.append(Bugs.author_id == user_id)
            elif key == "assignee":
                filters.append(Bugs.assignee_id == user_id)
            else:
                pass
    query = query.where(*filters)
    query = set_pagination(query, page, count_per_page)
    # TODO: set ordering
    execution = await session.execute(query)
    bugs = execution.scalars().all()
    return bugs


# bo = back office
async def bo_get_users_list(session: AsyncSession, token: common_schemas.Token):
    if token.admin is not True:
        raise exc.Forbidden("not an admin user")
    query = (
        select(Users)
        .options(selectinload(Users.comments))
        .options(selectinload(Users.raised_bugs))
        .options(selectinload(Users.assigned_bugs))
    )
    execution = await session.execute(query)
    users = execution.scalars().all()
    return users
