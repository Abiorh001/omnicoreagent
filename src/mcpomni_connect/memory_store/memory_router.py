from typing import Any
from mcpomni_connect.memory_store.in_memory import InMemoryStore


class MemoryRouter:
    def __init__(self, memory_store_type: str):
        if memory_store_type == "in_memory":
            self.memory_store = InMemoryStore()
        else:
            raise ValueError(f"Invalid memory store type: {memory_store_type}")

    def set_memory_config(self, mode: str, value: int = None) -> None:
        self.memory_store.set_memory_config(mode, value)

    async def store_message(
        self,
        role: str,
        content: str,
        metadata: dict | None = None,
        session_id: str = None,
    ) -> None:
        await self.memory_store.store_message(role, content, metadata, session_id)

    async def get_messages(
        self, session_id: str = None, agent_name: str = None
    ) -> list[dict[str, Any]]:
        return await self.memory_store.get_messages(session_id, agent_name)

    async def clear_memory(
        self, session_id: str = None, agent_name: str = None
    ) -> None:
        await self.memory_store.clear_memory(session_id, agent_name)
