import json
import time
from typing import Any, List
import redis.asyncio as redis
from decouple import config

from mcpomni_connect.memory_store.base import AbstractMemoryStore
from mcpomni_connect.utils import logger

REDIS_URL = config("REDIS_URL", default="redis://localhost:6379/0")


class RedisMemoryStore(AbstractMemoryStore):
    """Redis-backed memory store implementing AbstractMemoryStore interface."""

    def __init__(
        self,
        redis_client: redis.Redis | None = None,
    ) -> None:
        """Initialize Redis memory store.

        Args:
            redis_client: Optional Redis client instance
        """
        self._redis_client = redis_client or redis.from_url(
            REDIS_URL, decode_responses=True
        )
        self.memory_config: dict[str, Any] = {}

        logger.info("Initialized RedisMemoryStore")

    def set_memory_config(self, mode: str, value: int = None) -> None:
        """Set memory configuration.

        Args:
            mode: Memory mode ('sliding_window', 'token_budget')
            value: Optional value (e.g., window size or token limit)
        """
        valid_modes = {"sliding_window", "token_budget"}
        if mode.lower() not in valid_modes:
            raise ValueError(
                f"Invalid memory mode: {mode}. Must be one of {valid_modes}."
            )
        self.memory_config = {"mode": mode, "value": value}

    async def store_message(
        self,
        role: str,
        content: str,
        metadata: dict | None = None,
        session_id: str = None,
    ) -> None:
        """Store a message in Redis.

        Args:
            role: Message role (e.g., 'user', 'assistant')
            content: Message content
            metadata: Optional metadata about the message
            session_id: Session ID for grouping messages
        """
        try:
            metadata = metadata or {}
            logger.info(f"Storing message for session {session_id}: {content}")

            key = f"mcp_memory:{session_id}"
            timestamp = time.time()

            message = {
                "role": role,
                "content": str(content),
                "session_id": session_id,
                "msg_metadata": metadata,
                "timestamp": timestamp,
            }

            # Store as a JSON string in Redis
            await self._redis_client.zadd(key, {json.dumps(message): timestamp})

        except Exception as e:
            logger.error(f"Failed to store message: {e}")

    async def get_messages(
        self, session_id: str = None, agent_name: str = None
    ) -> List[dict]:
        """Get messages from Redis.

        Args:
            session_id: Session ID to get messages for
            agent_name: Optional agent name filter

        Returns:
            List of messages
        """
        try:

            key = f"mcp_memory:{session_id}"

            messages = await self._redis_client.zrange(key, 0, -1)

            result = [json.loads(msg) for msg in messages]
            # Apply memory configuration
            mode = self.memory_config.get("mode", "token_budget")
            value = self.memory_config.get("value")

            if mode.lower() == "sliding_window" and value is not None:
                result = result[-value:]
            elif mode.lower() == "token_budget" and value is not None:
                total_tokens = sum(len(str(msg["content"]).split()) for msg in result)
                while total_tokens > value and result:
                    result.pop(0)
                    total_tokens = sum(
                        len(str(msg["content"]).split()) for msg in result
                    )

            # Filter by agent name if specified
            if agent_name:
                result = [
                    msg
                    for msg in result
                    if msg.get("msg_metadata", {}).get("agent_name") == agent_name
                ]

            return result

        except Exception as e:
            logger.error(f"Failed to get messages: {e}")
            return []

    async def clear_memory(
        self, session_id: str = None, agent_name: str = None
    ) -> None:
        """Clear memory from Redis.

        Args:
            session_id: Session ID to clear (if None, clear all)
            agent_name: Optional agent name filter
        """
        try:
            if session_id and agent_name:
                # Clear messages for specific agent in specific session
                key = f"mcp_memory:{session_id}"
                messages = await self._redis_client.zrange(key, 0, -1)

                # Filter out messages for the specific agent
                filtered_messages = []
                for msg in messages:
                    msg_data = json.loads(msg)
                    if msg_data.get("msg_metadata", {}).get("agent_name") != agent_name:
                        filtered_messages.append(msg)

                # Delete the key and re-add filtered messages
                await self._redis_client.delete(key)
                if filtered_messages:
                    for msg in filtered_messages:
                        msg_data = json.loads(msg)
                        await self._redis_client.zadd(
                            key, {msg: msg_data.get("timestamp", 0)}
                        )

                logger.info(
                    f"Cleared memory for agent {agent_name} in session {session_id}"
                )

            elif session_id:
                # Clear all messages for specific session
                key = f"mcp_memory:{session_id}"
                await self._redis_client.delete(key)
                logger.info(f"Cleared memory for session {session_id}")

            elif agent_name:
                # Clear messages for specific agent across all sessions
                pattern = "mcp_memory:*"
                keys = await self._redis_client.keys(pattern)

                for key in keys:
                    messages = await self._redis_client.zrange(key, 0, -1)
                    filtered_messages = []

                    for msg in messages:
                        msg_data = json.loads(msg)
                        if (
                            msg_data.get("msg_metadata", {}).get("agent_name")
                            != agent_name
                        ):
                            filtered_messages.append(msg)

                    # Delete the key and re-add filtered messages
                    await self._redis_client.delete(key)
                    if filtered_messages:
                        for msg in filtered_messages:
                            msg_data = json.loads(msg)
                            await self._redis_client.zadd(
                                key, {msg: msg_data.get("timestamp", 0)}
                            )

                logger.info(
                    f"Cleared memory for agent {agent_name} across all sessions"
                )

            else:
                # Clear all memory - get all keys and delete them
                pattern = "mcp_memory:*"
                keys = await self._redis_client.keys(pattern)
                if keys:
                    await self._redis_client.delete(*keys)
                    logger.info(f"Cleared all memory ({len(keys)} sessions)")

        except Exception as e:
            logger.error(f"Failed to clear memory: {e}")

    def _serialize(self, data: Any) -> str:
        """Convert any non-serializable data into a JSON-compatible format."""
        try:
            return json.dumps(data, default=lambda o: o.__dict__)
        except Exception as e:
            logger.error(f"Serialization failed: {e}")
            return json.dumps({"error": "Serialization failed"})

    def _deserialize(self, data: Any) -> Any:
        """Convert stored JSON strings back to their original format if needed."""
        try:
            if "msg_metadata" in data:
                data["msg_metadata"] = json.loads(data["msg_metadata"])
            return data
        except Exception as e:
            logger.error(f"Deserialization failed: {e}")
            return data
