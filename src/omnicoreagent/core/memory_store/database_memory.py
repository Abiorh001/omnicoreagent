from omnicoreagent.core.memory_store.base import AbstractMemoryStore
from omnicoreagent.core.database.database_message_store import DatabaseMessageStore
from omnicoreagent.core.utils import logger
from typing import Optional


class DatabaseMemory(AbstractMemoryStore):
    def __init__(self, db_url: str = None):
        """
        Initialize the database memory store and set up the database message store service.
        """
        if db_url is None:
            raise ValueError("Database URL is required for DatabaseMemory")

        self.db_url = db_url

        self.db_session = DatabaseMessageStore(db_url=db_url)
        self.memory_config = {"mode": "sliding_window", "value": 10000}
        self.db_session.set_memory_config(
            self.memory_config["mode"], self.memory_config["value"]
        )

    def set_memory_config(self, mode: str, value: int = None) -> None:
        """
        Set memory configuration for both this instance and the underlying database session service.
        """
        self.memory_config["mode"] = mode
        self.memory_config["value"] = value
        self.db_session.set_memory_config(mode, value)

    async def store_message(
        self,
        role: str,
        content: str,
        metadata: dict | None = None,
        session_id: str = None,
    ) -> None:
        """
        Store a message in the database for the given session_id.
        """
        await self.db_session.store_message(
            role=role,
            content=content,
            metadata=metadata,
            session_id=session_id,
        )

    async def get_messages(self, session_id: str = None, agent_name: str = None):
        """
        Retrieve all messages for a given session_id from the database.
        Returns a list of message dicts.
        """
        return await self.db_session.get_messages(
            session_id=session_id, agent_name=agent_name
        )

    async def set_last_processed_messages(
        self, session_id: str, agent_name: str, timestamp: float, memory_type: str
    ) -> None:
        return await self.db_session.set_last_processed_messages(
            session_id, agent_name, timestamp, memory_type
        )

    async def get_last_processed_messages(
        self, session_id: str, agent_name: str, memory_type: str
    ) -> float | None:
        return await self.db_session.get_last_processed_messages(
            session_id, agent_name, memory_type
        )

    async def tool_exists(self, tool_name: str, mcp_server_name: str) -> Optional[dict]:
        """
        Check if a tool already exists for the given server.
        """
        return await self.db_session.tool_exists(
            tool_name=tool_name, mcp_server_name=mcp_server_name
        )

    async def store_tool(
        self,
        tool_name: str,
        mcp_server_name: str,
        raw_tool: dict,
        enriched_tool: dict,
    ) -> None:
        """
        Store a tool in the database.
        """
        await self.db_session.store_tool(
            tool_name=tool_name,
            mcp_server_name=mcp_server_name,
            raw_tool=raw_tool,
            enriched_tool=enriched_tool,
        )

    async def clear_memory(
        self,
        session_id: str = None,
        agent_name: str = None,
    ) -> None:
        """
        Delete messages for a session_id from the database.
        """
        await self.db_session.clear_memory(session_id=session_id, agent_name=agent_name)
