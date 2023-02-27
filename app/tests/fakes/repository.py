from typing import Any, Generic, Type
from uuid import UUID

from app.adapters.repository import AbstractRepository, ModelType
from app.domain import models


class FakeRepository(Generic[ModelType], AbstractRepository):
    def __init__(self, model: Type[ModelType]):
        self.db: dict[Any, Any] = dict()
        self.model = model
        self.seen = set()

    def _add(self, item: Type[ModelType]):
        self.db[item.id] = item  # type: ignore
        self.seen.add(item)

    def _add_all(self, items: list[Type[ModelType]]):
        for item in items:
            self.db[item.id] = item  # type: ignore
            self.seen.add(item)

    async def _get(self, ident: UUID):
        return self.db.get(ident)

    async def _remove(self, ident: UUID):
        model = await self._get(ident)
        if model:
            del self.db[ident]
        return

    async def _list(self, filters: dict[str, Any] | None = None):
        # customise for each individual repository
        return list(self.db.values())


class FakeUserRepository(FakeRepository[models.Users]):
    def __init__(self):
        super(FakeUserRepository, self).__init__(models.Users)

    async def _list(self, filters: dict[str, Any] | None = None):
        everything: list[models.Users] = list(self.db.values())
        if not filters:
            return everything
        else:
            out = []
            for key, val in filters.items():
                column, operator = key.split("__")
                try:
                    model_column = getattr(self.model, column)
                except AttributeError:
                    continue
                if model_column == "email" and operator == "eq":
                    out.extend([x for x in everything if x.email == val])
            return out


class FakeTagRepository(FakeRepository[models.Tags]):
    def __init__(self):
        super(FakeTagRepository, self).__init__(models.Tags)


class FakeBugRepository(FakeRepository[models.Bugs]):
    def __init__(self):
        super(FakeBugRepository, self).__init__(models.Bugs)


class FakeEventStoreRepository(FakeRepository[models.EventStore]):
    def __init__(self):
        super(FakeEventStoreRepository, self).__init__(models.EventStore)

    async def _get(self, ident: UUID):
        everything: list[models.EventStore] = list(self.db.values())
        return [x for x in everything if x.aggregate_id == ident]
