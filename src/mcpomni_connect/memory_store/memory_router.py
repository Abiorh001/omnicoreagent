from typing import Any
from decouple import config as decouple_config
from mcpomni_connect.memory_store.in_memory import InMemoryStore
from mcpomni_connect.memory_store.database_memory import DatabaseMemory
from mcpomni_connect.memory_store.redis_memory import RedisMemoryStore
from mcpomni_connect.utils import logger
from mcpomni_connect.utils import normalize_metadata
from mcpomni_connect.database.mongodb import MongoDb


class MemoryRouter:
    def __init__(self, memory_store_type: str):
        self.memory_store_type = memory_store_type
        if memory_store_type == "in_memory":
            self.memory_store = InMemoryStore()
        elif memory_store_type == "database":
            db_url = decouple_config(
                "DATABASE_URL", default="sqlite:///mcpomni_memory.db"
            )
            self.memory_store = DatabaseMemory(db_url=db_url)
        elif memory_store_type == "redis":
            self.memory_store = RedisMemoryStore()
        elif memory_store_type == "mongodb":
            uri = decouple_config("MONGODB_URI", default="mongodb://localhost:27017/")
            db_name = decouple_config("MONGODB_DB_NAME", default="mcpomni_connect")
            collection = decouple_config("MONGODB_COLLECTION", default="messages")
            self.memory_store = MongoDb(uri=uri, db_name=db_name, collection=collection)
        else:
            raise ValueError(f"Invalid memory store type: {memory_store_type}")

    def __str__(self):
        """Return a readable string representation of the MemoryRouter."""
        return f"MemoryRouter(type={self.memory_store_type}, store={type(self.memory_store).__name__})"

    def __repr__(self):
        """Return a detailed representation of the MemoryRouter."""
        return self.__str__()

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

    async def clear_memory(
        self, session_id: str = None, agent_name: str = None
    ) -> None:
        await self.memory_store.clear_memory(session_id, agent_name)

    def get_memory_store_info(self) -> dict[str, Any]:
        """Get information about the current memory store."""
        return {
            "type": self.memory_store_type,
            "available": True,
            "store_class": type(self.memory_store).__name__,
        }

    async def save_message_history_to_file(self, file_path: str) -> None:
        """Save message history to a file.

        Args:
            file_path: Path to save the message history
        """
        try:
            import json

            # Get all messages from all sessions
            all_messages = {}
            for session_id in self.memory_store.sessions_history.keys():
                messages = await self.get_messages(session_id)
                if messages:
                    all_messages[session_id] = messages

            with open(file_path, "w") as f:
                json.dump(all_messages, f, indent=2)
            logger.info(f"Message history saved to {file_path}")
        except Exception as e:
            logger.error(f"Failed to save message history: {e}")

    async def load_message_history_from_file(self, file_path: str) -> None:
        """Load message history from a file.

        Args:
            file_path: Path to load the message history from
        """
        try:
            import json

            with open(file_path, "r") as f:
                all_messages = json.load(f)

            # Restore messages to memory store
            for session_id, messages in all_messages.items():
                for message in messages:
                    await self.store_message(
                        role=message["role"],
                        content=message["content"],
                        metadata=message.get("metadata", {}),
                        session_id=session_id,
                    )
            logger.info(f"Message history loaded from {file_path}")
        except Exception as e:
            logger.error(f"Failed to load message history: {e}")
