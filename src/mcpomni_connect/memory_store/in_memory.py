from typing import Any
import asyncio
from mcpomni_connect.memory_store.base import AbstractMemoryStore
from mcpomni_connect.utils import logger


def _get_agent_name_from_metadata(metadata) -> str:
    """Extract agent name from metadata, handling both dict and ToolCallMetadata objects"""
    if not metadata:
        return None

    # Handle ToolCallMetadata objects (Pydantic models)
    if hasattr(metadata, "agent_name"):
        return metadata.agent_name

    # Handle dictionary metadata
    if isinstance(metadata, dict):
        return metadata.get("agent_name")

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
            metadata: Optional metadata about the message
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
                "metadata": metadata,
            }

            self.sessions_history[session_id].append(message)

        except Exception as e:
            logger.error(f"Failed to store message: {e}")

    async def get_messages(
        self, session_id: str = None, agent_name: str = None
    ) -> list[dict[str, Any]]:
        """Get messages from memory.

        Args:
            session_id: Session ID to get messages for
            agent_name: Optional agent name to filter by (from metadata)

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
            # Filter by agent_name if provided
            if agent_name:
                messages = [
                    msg
                    for msg in messages
                    if _get_agent_name_from_metadata(msg.get("metadata")) == agent_name
                ]

            return messages

        except Exception as e:
            logger.error(f"Failed to truncate message history: {e}")
            self.sessions_history[session_id] = []
            return []

    async def clear_memory(
        self, session_id: str = None, agent_name: str = None
    ) -> None:
        """Clear memory for a session or all memory.

        Args:
            session_id: Session ID to clear (if None, clear all)
            agent_name: Optional agent name to filter by
        """
        try:
            if session_id and session_id in self.sessions_history:
                if agent_name:
                    # Remove only messages for specific agent in this session
                    self.sessions_history[session_id] = [
                        msg
                        for msg in self.sessions_history[session_id]
                        if self._get_agent_name_from_metadata(msg.get("metadata"))
                        != agent_name
                    ]
                else:
                    # Remove entire session
                    del self.sessions_history[session_id]
            elif agent_name:
                # Remove messages for specific agent across all sessions
                for session_id in list(self.sessions_history.keys()):
                    self.sessions_history[session_id] = [
                        msg
                        for msg in self.sessions_history[session_id]
                        if self._get_agent_name_from_metadata(msg.get("metadata"))
                        != agent_name
                    ]
                    # Remove empty sessions
                    if not self.sessions_history[session_id]:
                        del self.sessions_history[session_id]
            else:
                # Clear all memory
                self.sessions_history = {}

        except Exception as e:
            logger.error(f"Failed to clear memory: {e}")
