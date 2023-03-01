from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.domain import enums
from app.domain.models import Users
from app.service import exceptions as exc
from app.service.users.dto import UserOut


async def get_my_user_page(session: AsyncSession, id: UUID):
    query = select(Users).where(Users.id == id, Users.user_status == enums.RecordStatusEnum.ACTIVE)
    execution = await session.execute(query)
    user = execution.scalars().first()
    if not user:
        raise exc.ItemNotFound(f"user with id {id} not found")
    return UserOut.from_orm(user)
