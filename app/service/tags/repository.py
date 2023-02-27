from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.repository import SqlAlchemyRepository
from app.domain.models import Tags


class TagRepository(SqlAlchemyRepository[Tags]):
    def __init__(self, session: AsyncSession):
        super(TagRepository, self).__init__(session, Tags)
