from app.service.unit_of_work import AbstractUnitOfWork
from app.tests.fakes.repository import (
    FakeBugRepository,
    FakeEventStoreRepository,
    FakeUserRepository,
)


class FakeUnitOfWork(AbstractUnitOfWork):
    def __init__(self):
        ...

    async def __aenter__(self) -> AbstractUnitOfWork:
        self.bugs = FakeBugRepository()
        self.users = FakeUserRepository()
        self.event_store = FakeEventStoreRepository()
        return await super().__aenter__()

    async def __aexit__(self, *args):
        return

    async def _commit(self):
        return

    async def _rollback(self):
        return

    async def _refresh(self, object):
        return

    def collect_new_events(self):
        objs = []
        objs.extend(list(self.bugs.seen))
        objs.extend(list(self.users.seen))
        for obj in objs:
            while obj.events:
                yield obj.events.popleft()
