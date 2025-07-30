from abc import ABC, abstractmethod
from typing import Generic, TypeVar

TMessage = TypeVar("TMessage")


class ABCQueueProducer(Generic[TMessage], ABC):
    @abstractmethod
    async def start(self) -> None: ...

    @abstractmethod
    def stop(self) -> None: ...

    @abstractmethod
    async def publish(self, request: TMessage) -> None: ...
