from typing import Any, Generic, Type
from uuid import UUID

from app.adapters.repository import AbstractRepository, ModelType
from app.domain import models


class FakeRepository(Generic[ModelType], AbstractRepository):
    def __init__(self, model: Type[ModelType]):
        self.session: dict[Any, Any] = dict()
        self.model = model
        self.seen = set()

    def _add(self, item: Type[ModelType]):
        self.session[item.id] = item  # type: ignore
        self.seen.add(item)

    def _add_all(self, items: list[Type[ModelType]]):
        for item in items:
            self.session[item.id] = item  # type: ignore
            self.seen.add(item)

    async def _get(self, ident: UUID):
        return self.session.get(ident)

    async def _remove(self, ident: UUID):
        model = await self._get(ident)
        if model:
            del self.session[ident]
        return

    async def _list(self, filters: dict[str, Any] | None = None, *args):
        # customise for each individual repository
        return list(self.session.values())


class FakeUserRepository(FakeRepository[models.Users]):
    def __init__(self):
        super(FakeUserRepository, self).__init__(models.Users)

    async def _list(self, *args, **kwargs):
        everything: list[models.Users] = list(self.session.values())
        if not args and not kwargs:
            return everything
        else:
            out: list[Any] = []
            for key, val in kwargs.items():
                column, operator = key.split("__")
                try:
                    getattr(self.model, column)
                except AttributeError:
                    continue
                if operator == "eq":
                    everything = [x for x in everything if getattr(self.model, column) == val]
            return out


class FakeBugRepository(FakeRepository[models.Bugs]):
    def __init__(self):
        super(FakeBugRepository, self).__init__(models.Bugs)


class FakeEventStoreRepository(FakeRepository[models.EventStore]):
    def __init__(self):
        super(FakeEventStoreRepository, self).__init__(models.EventStore)

    async def _get(self, ident: UUID):
        everything: list[models.EventStore] = list(self.session.values())
        return [x for x in everything if x.aggregate_id == ident]
