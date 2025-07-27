from typing import Any
import asyncio
from mcpomni_connect.memory_store.base import AbstractMemoryStore
from mcpomni_connect.utils import logger


def _get_agent_name_from_metadata(msg_metadata) -> str:
    # This function is now unused, but kept for compatibility if needed in the future.
    if not msg_metadata:
        return None
    if hasattr(msg_metadata, "agent_name"):
        return msg_metadata.agent_name
    if isinstance(msg_metadata, dict):
        return msg_metadata.get("agent_name")
    return None


class InMemoryStore(AbstractMemoryStore):
    """In memory store - Database compatible version"""

    def __init__(
        self,
    ) -> None:
        """Initialize memory storage.

        Args:
            max_context_tokens: Maximum tokens to keep in memory
            debug: Enable debug logging
        """
        # Changed to session-based storage for database compatibility
        self.sessions_history: dict[str, list[dict[str, Any]]] = {}
        self.memory_config: dict[str, Any] = {}

    def set_memory_config(self, mode: str, value: int = None) -> None:
        """Set global memory strategy.

        Args:
            mode: Memory mode ('sliding_window', 'token_budget')
            value: Optional value (e.g., window size or token limit)
        """
        valid_modes = {"sliding_window", "token_budget"}
        if mode.lower() not in valid_modes:
            raise ValueError(
                f"Invalid memory mode: {mode}. Must be one of {valid_modes}."
            )

        self.memory_config = {
            "mode": mode,
            "value": value,
        }

    async def store_message(
        self,
        role: str,
        content: str,
        metadata: dict | None = None,
        session_id: str = None,
    ) -> None:
        """Store a message in memory.

        Args:
            role: Message role (e.g., 'user', 'assistant')
            content: Message content
            msg_metadata: Optional metadata about the message
            session_id: Session ID for grouping messages
        """
        try:
            # Ensure metadata exists
            if metadata is None:
                metadata = {}

            # Use session-based storage for database compatibility
            if session_id not in self.sessions_history:
                self.sessions_history[session_id] = []

            message = {
                "role": role,
                "content": content,
                "session_id": session_id,
                "timestamp": asyncio.get_running_loop().time(),
                "msg_metadata": metadata,
            }
            logger.info(f"message: {message}")
            self.sessions_history[session_id].append(message)

        except Exception as e:
            logger.error(f"Failed to store message: {e}")

    async def get_messages(
        self, session_id: str, agent_name: str = None
    ) -> list[dict[str, Any]]:
        """Get messages from memory.

        Args:
            session_id: Session ID to get messages for

        Returns:
            List of messages
        """
        logger.info(f"get memory config: {self.memory_config}")
        try:
            if session_id not in self.sessions_history:
                self.sessions_history[session_id] = []
                return []

            messages = self.sessions_history[session_id]
            mode = self.memory_config.get("mode", "token_budget")
            value = self.memory_config.get("value")
            if mode.lower() == "sliding_window":
                messages = messages[-value:]

            elif mode.lower() == "token_budget":
                total_tokens = sum(len(str(msg["content"]).split()) for msg in messages)
                while value is not None and total_tokens > value and messages:
                    messages.pop(0)
                    total_tokens = sum(
                        len(str(msg["content"]).split()) for msg in messages
                    )
            logger.info(f"messages: {messages}")
            if agent_name:
                messages = [
                    msg
                    for msg in messages
                    if msg.get("msg_metadata", {}).get("agent_name") == agent_name
                ]
            logger.info(f"messages after agent name filter: {messages}")
            return messages

        except Exception as e:
            logger.error(f"Failed to truncate message history: {e}")
            self.sessions_history[session_id] = []
            return []

    async def clear_memory(self, session_id: str = None) -> None:
        """Clear memory for a session or all memory.

        Args:
            session_id: Session ID to clear (if None, clear all)
        """
        try:
            if session_id and session_id in self.sessions_history:
                del self.sessions_history[session_id]
            else:
                self.sessions_history = {}

        except Exception as e:
            logger.error(f"Failed to clear memory: {e}")
