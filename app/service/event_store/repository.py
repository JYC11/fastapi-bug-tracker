from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.repository import SqlAlchemyRepository
from app.domain.models import EventStore


class EventStoreRepository(SqlAlchemyRepository[EventStore]):
    def __init__(self, session: AsyncSession):
        super(EventStoreRepository, self).__init__(session, EventStore)

    async def _get(self, ident: UUID):
        _query = self.query.where(self.model.aggregate_id == ident)  # type: ignore
        res = await self.session.execute(_query)
        models: list[EventStore] = res.scalars().all()
        return models
