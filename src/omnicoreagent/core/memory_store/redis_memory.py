import json
from typing import Any, List, Optional
import redis.asyncio as redis
from decouple import config
import threading

from omnicoreagent.core.memory_store.base import AbstractMemoryStore
from omnicoreagent.core.utils import logger
from datetime import datetime, timezone

REDIS_URL = config("REDIS_URL", default=None)


class RedisConnectionManager:
    """
    Redis connection manager for efficient connection pooling and reuse.
    """

    _instance = None
    _lock = threading.RLock()

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "_initialized"):
            self._initialized = True
            self._client = None
            self._connection_count = 0
            logger.debug("RedisConnectionManager initialized")

    async def get_client(self) -> redis.Redis:
        """Get or create Redis client with connection pooling."""
        with self._lock:
            if self._client is None:
                try:
                    self._client = redis.from_url(
                        REDIS_URL,
                        decode_responses=True,
                        max_connections=20,  # Connection pool size
                        retry_on_timeout=True,
                        socket_timeout=5,
                        socket_connect_timeout=5,
                        health_check_interval=30,
                    )
                    logger.debug(
                        f"[RedisManager] Created Redis connection pool: {REDIS_URL}"
                    )
                except Exception as e:
                    logger.error(f"[RedisManager] Failed to create Redis client: {e}")
                    raise

            self._connection_count += 1
            logger.debug(
                f"[RedisManager] Redis connection usage count: {self._connection_count}"
            )
            return self._client

    def release_client(self):
        """Release a Redis client (decrement usage count)."""
        with self._lock:
            if self._connection_count > 0:
                self._connection_count -= 1
                logger.debug(
                    f"[RedisManager] Redis connection usage count: {self._connection_count}"
                )

    async def close_all(self):
        """Close all Redis connections."""
        with self._lock:
            if self._client:
                await self._client.close()
                self._client = None
                self._connection_count = 0
                logger.debug("[RedisManager] Closed all Redis connections")


# Global Redis connection manager
_redis_manager = None


def get_redis_manager():
    """Get the global Redis connection manager instance."""
    global _redis_manager
    if _redis_manager is None:
        _redis_manager = RedisConnectionManager()
    return _redis_manager


class RedisMemoryStore(AbstractMemoryStore):
    """Redis-backed memory store implementing AbstractMemoryStore interface."""

    def __init__(
        self,
        redis_url: str = None,
    ) -> None:
        """Initialize Redis memory store.

        Args:
            redis_url: Redis connection URL. If None, Redis will not be initialized.
        """
        if redis_url is None:
            logger.debug("RedisMemoryStore skipped - redis_url not provided")
            self._connection_manager = None
            self._redis_client = None
            self.memory_config: dict[str, Any] = {}
            return

        # Set the global REDIS_URL for the connection manager
        global REDIS_URL
        REDIS_URL = redis_url

        # Use connection manager for production
        self._connection_manager = get_redis_manager()
        self._redis_client = None
        self.memory_config: dict[str, Any] = {}
        logger.debug(f"Initialized RedisMemoryStore with redis_url: {redis_url}")

    async def _get_client(self) -> redis.Redis:
        """Get Redis client from connection manager or direct client."""
        if self._connection_manager:
            return await self._connection_manager.get_client()
        elif self._redis_client:
            return self._redis_client
        else:
            raise RuntimeError("Redis not configured - REDIS_URL not set")

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
        client = None
        try:
            client = await self._get_client()
            metadata = metadata or {}

            key = f"omnicoreagent_memory:{session_id}"

            dt = datetime.now(timezone.utc)  # timezone-aware UTC
            timestamp_iso = dt.isoformat()
            timestamp_score = dt.timestamp()  # float (epoch seconds)

            message = {
                "role": role,
                "content": str(content),
                "session_id": session_id,
                "msg_metadata": metadata,
                "timestamp": timestamp_iso,  # keep ISO in the payload
            }

            await client.zadd(key, {json.dumps(message): timestamp_score})
            logger.debug(f"Stored message for session {session_id}")

        except Exception as e:
            logger.error(f"Failed to store message: {e}")
        finally:
            if self._connection_manager and client:
                self._connection_manager.release_client()

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
        client = None
        try:
            client = await self._get_client()
            key = f"omnicoreagent_memory:{session_id}"

            # Get all messages for the session
            raw_messages = await client.zrange(key, 0, -1)

            if not raw_messages:
                return []

            # Parse and filter messages
            result = []
            for msg_json in raw_messages:
                try:
                    msg = json.loads(msg_json)
                    # Filter by agent name if specified (at parsing level for efficiency)
                    if (
                        agent_name
                        and msg.get("msg_metadata", {}).get("agent_name") != agent_name
                    ):
                        continue
                    result.append(msg)
                except json.JSONDecodeError:
                    logger.warning(f"Failed to parse message JSON: {msg_json}")
                    continue

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

            return result

        except Exception as e:
            logger.error(f"Failed to get messages: {e}")
            return []
        finally:
            if self._connection_manager and client:
                self._connection_manager.release_client()

    async def set_last_processed_messages(
        self, session_id: str, agent_name: str, timestamp: float, memory_type: str
    ) -> None:
        """Set the last processed timestamp for a given session/agent."""
        # These methods are called from background processing/external threads
        # They need fresh connections to avoid sharing with main thread
        client = None
        try:
            if self._connection_manager:
                # Background processing - get fresh connection
                client = redis.from_url(
                    REDIS_URL,
                    decode_responses=True,
                    max_connections=1,  # Single connection for background
                    socket_timeout=30,
                    socket_connect_timeout=30,
                )
            else:
                # Direct client mode
                client = self._redis_client

            key = f"mcp_last_processed:{session_id}:{agent_name}:{memory_type}"
            await client.set(key, str(timestamp))
            logger.debug(
                f"Set last processed timestamp for {session_id}:{agent_name}:{memory_type}"
            )

        except Exception as e:
            logger.error(f"Failed to set last processed: {e}")
        finally:
            # Close fresh connection for background processing
            if self._connection_manager and client and hasattr(client, "close"):
                await client.close()

    async def get_last_processed_messages(
        self, session_id: str, agent_name: str, memory_type: str
    ) -> Optional[float]:
        """Get the last processed timestamp for a given session/agent."""
        # These methods are called from background processing/external threads
        # They need fresh connections to avoid sharing with main thread
        client = None
        try:
            if self._connection_manager:
                # Background processing - get fresh connection
                client = redis.from_url(
                    REDIS_URL,
                    decode_responses=True,
                    max_connections=1,  # Single connection for background
                    socket_timeout=30,
                    socket_connect_timeout=30,
                )
            else:
                # Direct client mode
                client = self._redis_client

            key = f"mcp_last_processed:{session_id}:{agent_name}:{memory_type}"
            ts_str = await client.get(key)

            if ts_str:
                return ts_str
            return None
        except Exception as e:
            logger.error(f"Failed to get last processed: {e}")
            return None
        finally:
            # Close fresh connection for background processing
            if self._connection_manager and client and hasattr(client, "close"):
                await client.close()

    async def tool_exists(self, tool_name: str, mcp_server_name: str) -> Optional[dict]:
        """
        Check if a tool exists in Redis for a given MCP server.
        Returns the tool dict if it exists, else False.
        """
        try:
            client = await self._get_client()
            key = f"mcp_tools:{mcp_server_name}:{tool_name}"
            data = await client.get(key)
            if data is not None:
                # Decode bytes to str and load JSON
                tool = json.loads(data)
                return tool
            return None
        except Exception as e:
            logger.error(f"Failed to check tool existence: {e}")
            return None

        finally:
            if self._connection_manager and client:
                self._connection_manager.release_client()

    async def store_tool(
        self,
        tool_name: str,
        mcp_server_name: str,
        raw_tool: dict,
        enriched_tool: dict,
    ) -> None:
        """
        Store a tool in Redis for a given MCP server.
        """
        client = None
        try:
            client = await self._get_client()
            key = f"mcp_tools:{mcp_server_name}:{tool_name}"
            value = json.dumps(
                {
                    "tool_name": tool_name,
                    "mcp_server_name": mcp_server_name,
                    "raw_tool": raw_tool,
                    "enriched_tool": enriched_tool,
                }
            )
            await client.set(key, value)
            logger.debug(f"Stored tool {tool_name} for MCP server {mcp_server_name}")
        except Exception as e:
            logger.error(f"Failed to store tool {tool_name}: {e}")
        finally:
            if self._connection_manager and client:
                self._connection_manager.release_client()

    async def clear_memory(
        self, session_id: str = None, agent_name: str = None
    ) -> None:
        """Clear memory from Redis with optimized operations.

        Args:
            session_id: Session ID to clear (if None, clear all)
            agent_name: Optional agent name filter
        """
        client = None
        try:
            client = await self._get_client()

            if session_id and agent_name:
                # Clear messages for specific agent in specific session
                await self._clear_agent_from_session(client, session_id, agent_name)

            elif session_id:
                # Clear all messages for specific session
                key = f"mcp_memory:{session_id}"
                await client.delete(key)
                logger.debug(f"Cleared memory for session {session_id}")

            elif agent_name:
                # Clear messages for specific agent across all sessions
                await self._clear_agent_across_sessions(client, agent_name)

            else:
                # Clear all memory - get all keys and delete them
                pattern = "mcp_memory:*"
                keys = await client.keys(pattern)
                if keys:
                    await client.delete(*keys)
                    logger.debug(f"Cleared all memory ({len(keys)} sessions)")

        except Exception as e:
            logger.error(f"Failed to clear memory: {e}")
        finally:
            if self._connection_manager and client:
                self._connection_manager.release_client()

    async def _clear_agent_from_session(
        self, client: redis.Redis, session_id: str, agent_name: str
    ) -> None:
        """Efficiently clear messages for a specific agent from a session."""
        key = f"mcp_memory:{session_id}"
        messages = await client.zrange(key, 0, -1, withscores=True)

        if not messages:
            logger.debug(f"No messages found for session {session_id}")
            return

        # Parse messages and filter out the target agent
        to_remove = []
        to_keep = []

        for msg_json, score in messages:
            try:
                msg_data = json.loads(msg_json)
                if msg_data.get("msg_metadata", {}).get("agent_name") == agent_name:
                    to_remove.append(msg_json)
                else:
                    to_keep.append((msg_json, score))
            except json.JSONDecodeError:
                logger.warning(f"Failed to parse message JSON: {msg_json}")
                continue

        if to_remove:
            # Remove specific messages by their JSON content
            await client.zrem(key, *to_remove)

            # Re-add the kept messages (this is still necessary for Redis sorted sets)
            if to_keep:
                for msg_json, score in to_keep:
                    await client.zadd(key, {msg_json: score})

            logger.debug(
                f"Cleared {len(to_remove)} messages for agent {agent_name} in session {session_id}"
            )
        else:
            logger.debug(
                f"No messages found for agent {agent_name} in session {session_id}"
            )

    async def _clear_agent_across_sessions(
        self, client: redis.Redis, agent_name: str
    ) -> None:
        """Efficiently clear messages for a specific agent across all sessions."""
        pattern = "mcp_memory:*"
        keys = await client.keys(pattern)

        if not keys:
            logger.debug("No session keys found")
            return

        total_removed = 0
        for key in keys:
            messages = await client.zrange(key, 0, -1, withscores=True)

            if not messages:
                continue

            # Parse and filter messages for this session
            to_remove = []
            to_keep = []

            for msg_json, score in messages:
                try:
                    msg_data = json.loads(msg_json)
                    if msg_data.get("msg_metadata", {}).get("agent_name") == agent_name:
                        to_remove.append(msg_json)
                    else:
                        to_keep.append((msg_json, score))
                except json.JSONDecodeError:
                    logger.warning(f"Failed to parse message JSON: {msg_json}")
                    continue

            if to_remove:
                # Remove specific messages and re-add kept ones
                await client.zrem(key, *to_remove)
                if to_keep:
                    for msg_json, score in to_keep:
                        await client.zadd(key, {msg_json: score})

                total_removed += len(to_remove)
                logger.debug(
                    f"Cleared {len(to_remove)} messages for agent {agent_name} in {key}"
                )

        logger.debug(
            f"Cleared {total_removed} messages for agent {agent_name} across all sessions"
        )

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
