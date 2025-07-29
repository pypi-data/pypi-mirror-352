from abc import ABC, abstractmethod


class BaseStep(ABC):
    @abstractmethod
    async def run(self) -> None:
        pass
