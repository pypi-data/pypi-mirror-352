from abc import ABCMeta, abstractmethod
from typing import Any, Generic, TypeVar
from uuid import UUID

TEntity = TypeVar("TEntity")


class ABCAsyncGenericRepository(Generic[TEntity], metaclass=ABCMeta):
    @abstractmethod
    async def get_all(self, **filters: Any) -> list[TEntity]: ...

    @abstractmethod
    async def get(self, **filters: Any) -> TEntity | None: ...

    @abstractmethod
    async def create(self, entity: TEntity) -> TEntity: ...

    @abstractmethod
    async def create_many(self, entities: list[TEntity]) -> list[TEntity]: ...

    @abstractmethod
    async def update(self, id: UUID, entity: TEntity) -> bool: ...

    @abstractmethod
    async def delete(self, id: UUID) -> bool: ...
