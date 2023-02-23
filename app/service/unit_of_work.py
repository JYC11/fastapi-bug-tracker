import abc

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.exc import StaleDataError

from app.adapters.repository import ModelType, SqlAlchemyRepository
from app.common.db import async_transactional_session_factory
from app.domain.models import Bugs, Tags, Users
from app.service import exceptions

DEFAULT_TRANSACTIONAL_FACTORY = async_transactional_session_factory


class AbstractUnitOfWork(abc.ABC):
    async def __aenter__(self) -> "AbstractUnitOfWork":
        return self

    async def commit(self):
        await self._commit()

    async def rollback(self):
        await self._rollback()

    async def refresh(self, object: ModelType):
        await self._refresh(object)

    @abc.abstractmethod
    async def _commit(self):
        raise NotImplementedError

    @abc.abstractmethod
    async def _rollback(self):
        raise NotImplementedError

    @abc.abstractmethod
    async def _refresh(self, object: ModelType):
        raise NotImplementedError

    @abc.abstractmethod
    def collect_new_events(self):
        raise NotImplementedError


class SqlAlchemyUnitOfWork(AbstractUnitOfWork):
    def __init__(self, session_factory=DEFAULT_TRANSACTIONAL_FACTORY):
        self.session_factory = session_factory

    async def __aenter__(self) -> AbstractUnitOfWork:
        self.session: AsyncSession = self.session_factory()
        self.bugs = SqlAlchemyRepository(model=Bugs, session=self.session)
        self.tags = SqlAlchemyRepository(model=Tags, session=self.session)
        self.users = SqlAlchemyRepository(model=Users, session=self.session)
        return await super().__aenter__()

    async def __aexit__(self, *args):
        await self.session.rollback()
        await self.session.close()

    async def _commit(self):
        try:
            await self.session.commit()
        except StaleDataError:
            await self.session.rollback()
            raise exceptions.ConcurrencyException

    async def _rollback(self):
        await self.session.rollback()

    async def _refresh(self, object):
        await self.session.refresh(object)

    def collect_new_events(self):
        raise NotImplementedError
