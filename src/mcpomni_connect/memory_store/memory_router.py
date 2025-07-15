import os
from typing import Any, Optional
from mcpomni_connect.memory_store.in_memory import InMemoryStore
from mcpomni_connect.memory_store.database_memory import DatabaseMemory
from mcpomni_connect.session.database_session import DatabaseSessionService


class MemoryRouter:
    def __init__(self, memory_store_type: str):
        if memory_store_type == "in_memory":
            self.memory_store = InMemoryStore()
        elif memory_store_type=="database":
            db_url=os.getenv("DATABASE_URL") or "sqlite:///mcpomni_memory.db"
            self.memory_store=DatabaseMemory(db_url=db_url)
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
        self, session_id: str = None, agent_name: str = None, user_id: Optional[str] = None, app_name: Optional[str] = None
    ) -> list[dict[str, Any]]:
        if isinstance(self.memory_store, InMemoryStore):
            return await self.memory_store.get_messages(session_id, agent_name)
        elif isinstance(self.memory_store, DatabaseMemory):
            if user_id is None or app_name is None:
                raise ValueError("user_id and app_name must be provided for database memory store")
            events = await self.memory_store.get_messages(user_id, app_name, session_id)
            return [event.dict() for event in events]
        else:
            return []  # Default return for unexpected memory store types

    async def clear_memory(
        self, session_id: str = None, agent_name: str = None
    ) -> None:
        await self.memory_store.clear_memory(session_id, agent_name)
