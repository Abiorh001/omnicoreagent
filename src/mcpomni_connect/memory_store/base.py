from abc import ABC, abstractmethod
from typing import List


class AbstractMemoryStore(ABC):
    @abstractmethod
    def set_memory_config(self, mode: str, value: int = None) -> None:
        pass

    @abstractmethod
    async def store_message(
        self,
        role: str,
        content: str,
        metadata: dict | None = None,
        session_id: str = None,
    ) -> None:
        pass

    @abstractmethod
    async def get_messages(
        self, session_id: str = None, agent_name: str = None
    ) -> List[dict]:
        pass

    @abstractmethod
    async def clear_memory(
        self, session_id: str = None, agent_name: str = None
    ) -> None:
        pass
