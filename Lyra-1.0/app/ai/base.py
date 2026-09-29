from abc import ABC, abstractmethod


class AIProvider(ABC):

    @abstractmethod
    async def respond(self, text: str) -> str:
        raise NotImplementedError