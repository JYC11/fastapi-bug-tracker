from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy.sql.selectable import Select

from app.adapters.repository import SqlAlchemyRepository
from app.domain.models import Users


class UserRepository(SqlAlchemyRepository[Users]):
    def __init__(self, session: AsyncSession):
        super(UserRepository, self).__init__(session, Users)
        self.query: Select = (
            select(Users)
            .options(selectinload(Users.comments))
            .options(selectinload(Users.raised_bugs))
            .options(selectinload(Users.assigned_bugs))
        )
