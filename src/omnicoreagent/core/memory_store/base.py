from abc import ABC, abstractmethod
from typing import List, Optional


class AbstractMemoryStore(ABC):
    @abstractmethod
    def set_memory_config(self, mode: str, value: int = None) -> None:
        raise NotImplementedError

    @abstractmethod
    async def store_message(
        self,
        role: str,
        content: str,
        metadata: dict,
        session_id: str,
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    async def get_messages(
        self, session_id: str = None, agent_name: str = None
    ) -> List[dict]:
        raise NotImplementedError

    @abstractmethod
    async def set_last_processed_messages(
        self, session_id: str, agent_name: str, timestamp: float, memory_type: str
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    async def get_last_processed_messages(
        self, session_id: str, agent_name: str, memory_type: str
    ) -> Optional[float]:
        raise NotImplementedError

    @abstractmethod
    async def tool_exists(self, tool_name: str, mcp_server_name: str) -> Optional[dict]:
        raise NotImplementedError

    @abstractmethod
    async def store_tool(
        self,
        tool_name: str,
        mcp_server_name: str,
        raw_tool: dict,
        enriched_tool: dict,
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    async def clear_memory(
        self, session_id: str = None, agent_name: str = None
    ) -> None:
        raise NotImplementedError
