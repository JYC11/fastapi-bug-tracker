import abc
from typing import Any, Generic, Type, TypeVar
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.sql.selectable import Select

ModelType = TypeVar("ModelType", bound=object)


class AbstractRepository(abc.ABC):
    def __init__(self):
        self.session: AsyncSession | Any
        self.seen = set()

    @abc.abstractmethod
    def _add(self, item: Any):
        ...

    @abc.abstractmethod
    def _add_all(self, items: list[Any]):
        ...

    @abc.abstractmethod
    def _get(self, ident: Any):
        ...

    @abc.abstractmethod
    def _remove(self, ident: Any):
        ...

    @abc.abstractmethod
    def _list(self, filters: dict[str, Any] | None = None):
        ...

    def add(self, item: Any):
        self._add(item)

    def add_all(self, items: list[Any]):
        self._add_all(items)

    async def get(self, ident: Any):
        return await self._get(ident)

    async def remove(self, ident: Any):
        return await self._remove(ident)

    async def list(self, filters: dict[str, Any] | None = None):
        return await self._list(filters)


class SqlAlchemyRepository(Generic[ModelType], AbstractRepository):
    def __init__(self, session: AsyncSession, model: Type[ModelType]):
        self.session = session
        self.model = model
        self.seen = set()
        self.query: Select = select(self.model)

    def _add(self, item: Type[ModelType]):
        self.session.add(item)
        self.seen.add(item)

    def _add_all(self, items: list[Type[ModelType]]):
        self.session.add_all(items)
        for item in items:
            self.seen.add(item)

    async def _get(self, ident: UUID) -> Type[ModelType] | None:
        _query = self.query.where(self.model.id == ident)  # type: ignore
        execution = await self.session.execute(_query)
        model: Type[ModelType] | None = execution.scalars().first()
        return model

    async def _remove(self, ident: UUID):
        model = await self._get(ident)
        if model:
            await self.session.delete(model)
        return

    async def _list(self, filters: dict[str, Any] | None = None) -> list[Type[ModelType]]:
        if not filters:
            execution = await self.session.execute(self.query)
            models = execution.scalars().all()
            return models
        _filters = []
        for key, value in filters.items():
            column, operator = key.split("__")
            try:
                model_column = getattr(self.model, column)
            except AttributeError:
                continue
            if operator == "eq":
                _filters.append(model_column == value)
            elif operator == "not_eq":
                _filters.append(model_column != value)
            elif operator == "gt":
                _filters.append(model_column > value)
            elif operator == "gte":
                _filters.append(model_column >= value)
            elif operator == "lt":
                _filters.append(model_column < value)
            elif operator == "lte":
                _filters.append(model_column <= value)
            elif operator == "in":
                _filters.append(model_column.in_(value))
            elif operator == "not_in":
                _filters.append(model_column.not_in(value))
            elif operator == "btw":
                _filters.append(model_column.between(*value))
            elif operator == "like":
                _filters.append(model_column.like(f"%{value}%"))
            elif operator == "is":
                _filters.append(model_column.is_(value))

        _query = self.query.where(*_filters)
        execution = await self.session.execute(_query)
        models = execution.scalars().all()
        return models
