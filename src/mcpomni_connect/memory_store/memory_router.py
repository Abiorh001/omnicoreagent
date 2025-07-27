import os
from typing import Any
from mcpomni_connect.memory_store.in_memory import InMemoryStore
from mcpomni_connect.memory_store.database_memory import DatabaseMemory
from mcpomni_connect.memory_store.redis_memory import RedisMemoryStore
from mcpomni_connect.utils import logger
from mcpomni_connect.utils import normalize_metadata


class MemoryRouter:
    def __init__(self, memory_store_type: str):
        if memory_store_type == "in_memory":
            self.memory_store = InMemoryStore()
        elif memory_store_type == "database":
            db_url = os.getenv("DATABASE_URL") or "sqlite:///mcpomni_memory.db"
            self.memory_store = DatabaseMemory(db_url=db_url)
        elif memory_store_type == "redis":
            self.memory_store = RedisMemoryStore()
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
        if metadata is not None:
            metadata = normalize_metadata(metadata)
        await self.memory_store.store_message(role, content, metadata, session_id)

    async def get_messages(
        self, session_id: str, agent_name: str = None
    ) -> list[dict[str, Any]]:
        messages = await self.memory_store.get_messages(session_id, agent_name)
        # convert from msg_metadata to metadata
        for message in messages:
            message["metadata"] = message.pop("msg_metadata", None)
        return messages

    async def clear_memory(self, session_id: str = None) -> None:
        await self.memory_store.clear_memory(session_id)
