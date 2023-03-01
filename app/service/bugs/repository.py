from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.sql.selectable import Select

from app.adapters.repository import SqlAlchemyRepository
from app.domain.models import Bugs


class BugRepository(SqlAlchemyRepository[Bugs]):
    def __init__(self, session: AsyncSession):
        super(BugRepository, self).__init__(session, Bugs)
        self.query: Select = (
            select(Bugs)
            .options(joinedload(Bugs.comments))
            .options(selectinload(Bugs.author))
            .options(selectinload(Bugs.assignee))
        )
