from typing import Any, Generic, Protocol, TypeVar


class MappedEntity(Protocol):
    id: Any


T = TypeVar('T', bound=MappedEntity)


class BaseRepositoryProtocol(Protocol, Generic[T]):
    async def get(self, id: int) -> T | None: ...
    async def create(self, obj: T) -> T: ...
    async def update(self, obj: T) -> T: ...
    async def list(
        self,
        offset: int = 0,
        limit: int = 20,
    ) -> list[T]: ...
    async def delete(self, id: int) -> None: ...