"""
Background OmniAgent for self-flying automation.
"""

import asyncio
import uuid
from typing import Any, Dict, List, Optional
from datetime import datetime

from omnicoreagent.omni_agent.agent import OmniAgent

from omnicoreagent.core.memory_store.memory_router import MemoryRouter

from omnicoreagent.core.utils import logger
from omnicoreagent.core.events.event_router import EventRouter
from omnicoreagent.core.events.base import (
    Event,
    EventType,
    BackgroundTaskStartedPayload,
    BackgroundTaskCompletedPayload,
    BackgroundTaskErrorPayload,
    BackgroundAgentStatusPayload,
)
from omnicoreagent.omni_agent.background_agent.task_registry import TaskRegistry


class BackgroundOmniAgent(OmniAgent):
    """Background OmniAgent for automated task execution."""

    def __init__(
        self,
        config: Dict[str, Any],
        task_registry: TaskRegistry,
        memory_router: Optional[MemoryRouter] = None,
        event_router: Optional[EventRouter] = None,
    ):
        """
        Initialize BackgroundOmniAgent.

        Args:
            config: Configuration dictionary containing agent setup
            memory_store: Optional memory store
            event_router: Optional event router for event streaming
            task_registry: TaskRegistry instance (required for task management)
        """
        # Extract agent configuration
        agent_config = config.get("agent_config", {})
        model_config = config.get("model_config", {})
        mcp_tools = config.get("mcp_tools", [])
        local_tools = config.get("local_tools", None)  # ToolRegistry instance

        # Initialize base OmniAgent with all components
        super().__init__(
            name=config.get("agent_id", f"background_agent_{uuid.uuid4().hex[:8]}"),
            system_instruction=config.get(
                "system_instruction",
                "You are a background agent that executes tasks automatically.",
            ),
            model_config=model_config,
            mcp_tools=mcp_tools,
            local_tools=local_tools,  # Pass ToolRegistry instance
            agent_config=agent_config,
            memory_router=memory_router,
            event_router=event_router,
            debug=config.get("debug", False),
        )

        # Background-specific attributes
        self.agent_id = config.get("agent_id", self.name)
        self.interval = config.get("interval", 3600)  # Default: 1 hour
        self.max_retries = config.get("max_retries", 3)
        self.retry_delay = config.get("retry_delay", 60)  # seconds

        # Task registry integration (required)
        if task_registry is None:
            raise ValueError("TaskRegistry is required for BackgroundOmniAgent")
        self.task_registry = task_registry

        # Generate persistent session_id for this agent instance
        self.session_id = f"background_{self.agent_id}_{uuid.uuid4().hex[:8]}"

        # State
        self.is_running = False
        self.last_run = None
        self.run_count = 0
        self.error_count = 0

        logger.info(
            f"Initialized BackgroundOmniAgent: {self.agent_id} with session_id: {self.session_id}"
        )

    async def connect_mcp_servers(self):
        """Connect to MCP servers if not already connected."""
        await super().connect_mcp_servers()
        logger.info(f"BackgroundOmniAgent {self.agent_id} connected to MCP servers")

    def get_session_id(self) -> str:
        """Get the persistent session ID for this background agent."""
        return self.session_id

    def get_event_stream_info(self) -> Dict[str, Any]:
        """Get information needed for event streaming setup."""
        return {
            "agent_id": self.agent_id,
            "session_id": self.session_id,
            "event_store_type": self.get_event_store_type(),
            "event_store_available": self.is_event_store_available(),
            "event_store_info": self.get_event_store_info(),
        }

    async def stream_events(self, session_id: str):
        """Stream events for this background agent (consistent with OmniAgent API)."""
        async for event in self.event_router.stream(session_id=session_id):
            yield event

    async def get_events(self, session_id: str) -> List[Event]:
        """Get events for this background agent (consistent with OmniAgent API)."""
        return await self.event_router.get_events(session_id=session_id)

    def get_task_query(self) -> str:
        """Get the task query from TaskRegistry."""
        if not self.task_registry.exists(self.agent_id):
            raise ValueError(
                f"No task registered for agent {self.agent_id}. Use TaskRegistry to register a task first."
            )

        task_config = self.task_registry.get(self.agent_id)
        if not task_config or "query" not in task_config:
            raise ValueError(f"Task for agent {self.agent_id} is missing 'query' field")

        logger.info(f"Using task query from TaskRegistry for agent {self.agent_id}")
        return task_config["query"]

    def get_task_config(self) -> Dict[str, Any]:
        """Get the complete task configuration from TaskRegistry."""
        if not self.task_registry.exists(self.agent_id):
            raise ValueError(
                f"No task registered for agent {self.agent_id}. Use TaskRegistry to register a task first."
            )

        task_config = self.task_registry.get(self.agent_id)
        if not task_config:
            raise ValueError(f"Task configuration not found for agent {self.agent_id}")

        logger.info(f"Using task config from TaskRegistry for agent {self.agent_id}")
        return task_config

    def has_task(self) -> bool:
        """Check if the agent has a task registered."""
        return self.task_registry.exists(self.agent_id)

    async def run_task(self, **kwargs):
        """Execute the background task."""
        if self.is_running:
            logger.warning(
                f"Agent {self.agent_id} is already running, skipping execution"
            )
            return

        # Check if task is registered
        if not self.has_task():
            raise ValueError(
                f"No task registered for agent {self.agent_id}. Register a task first using TaskRegistry."
            )

        self.is_running = True
        # Use the main session_id for consistency - don't create new session IDs for each run
        task_session_id = self.session_id

        try:
            # Emit task started event using EventRouter
            task_started_event = Event(
                type=EventType.BACKGROUND_TASK_STARTED,
                payload=BackgroundTaskStartedPayload(
                    agent_id=self.agent_id,
                    session_id=task_session_id,
                    timestamp=datetime.now().isoformat(),
                    run_count=self.run_count + 1,
                    kwargs=kwargs,
                ),
                agent_name=self.agent_id,
            )
            await self.event_router.append(
                session_id=task_session_id, event=task_started_event
            )

            # Emit agent status event
            status_event = Event(
                type=EventType.BACKGROUND_AGENT_STATUS,
                payload=BackgroundAgentStatusPayload(
                    agent_id=self.agent_id,
                    status="running",
                    session_id=task_session_id,
                    timestamp=datetime.now().isoformat(),
                ),
                agent_name=self.agent_id,
            )
            await self.event_router.append(
                session_id=task_session_id, event=status_event
            )

            # Execute task with retries
            result = await self._execute_with_retries(**kwargs)

            # Update metrics
            self.run_count += 1
            self.last_run = datetime.now()

            # Emit task completed event
            task_completed_event = Event(
                type=EventType.BACKGROUND_TASK_COMPLETED,
                payload=BackgroundTaskCompletedPayload(
                    agent_id=self.agent_id,
                    session_id=task_session_id,
                    timestamp=datetime.now().isoformat(),
                    run_count=self.run_count,
                    result=result,
                ),
                agent_name=self.agent_id,
            )
            await self.event_router.append(
                session_id=task_session_id, event=task_completed_event
            )

            # Emit agent status event
            status_event = Event(
                type=EventType.BACKGROUND_AGENT_STATUS,
                payload=BackgroundAgentStatusPayload(
                    agent_id=self.agent_id,
                    status="idle",
                    last_run=self.last_run.isoformat(),
                    run_count=self.run_count,
                    timestamp=datetime.now().isoformat(),
                ),
                agent_name=self.agent_id,
            )
            await self.event_router.append(
                session_id=task_session_id, event=status_event
            )

            logger.info(f"Background task completed for agent {self.agent_id}")
            return result

        except Exception as e:
            self.error_count += 1

            # Emit error event
            error_event = Event(
                type=EventType.BACKGROUND_TASK_ERROR,
                payload=BackgroundTaskErrorPayload(
                    agent_id=self.agent_id,
                    session_id=task_session_id,
                    timestamp=datetime.now().isoformat(),
                    error=str(e),
                    error_count=self.error_count,
                ),
                agent_name=self.agent_id,
            )
            await self.event_router.append(
                session_id=task_session_id, event=error_event
            )

            # Emit agent status event
            status_event = Event(
                type=EventType.BACKGROUND_AGENT_STATUS,
                payload=BackgroundAgentStatusPayload(
                    agent_id=self.agent_id,
                    status="error",
                    last_run=self.last_run.isoformat() if self.last_run else None,
                    run_count=self.run_count,
                    error_count=self.error_count,
                    timestamp=datetime.now().isoformat(),
                ),
                agent_name=self.agent_id,
            )
            await self.event_router.append(
                session_id=task_session_id, event=status_event
            )

            logger.error(f"Background task failed for agent {self.agent_id}: {e}")
            raise

        finally:
            self.is_running = False

    async def _execute_with_retries(self, **kwargs):
        """Execute task with retry logic."""
        last_error = None

        for attempt in range(self.max_retries + 1):
            try:
                # Get task query from TaskRegistry (no fallback)
                task_query = kwargs.get("query") or self.get_task_query()

                # Run the agent using the base OmniAgent run method with consistent session_id
                result = await self.run(
                    query=task_query,
                    session_id=self.session_id,  # Use consistent session_id
                )

                return result

            except Exception as e:
                last_error = e
                logger.warning(
                    f"Attempt {attempt + 1} failed for agent {self.agent_id}: {e}"
                )

                if attempt < self.max_retries:
                    await asyncio.sleep(self.retry_delay)
                else:
                    break

        # All retries exhausted
        raise last_error

    def get_status(self) -> Dict[str, Any]:
        """Get current status of the background agent."""
        return {
            "agent_id": self.agent_id,
            "session_id": self.session_id,
            "is_running": self.is_running,
            "last_run": self.last_run.isoformat() if self.last_run else None,
            "run_count": self.run_count,
            "error_count": self.error_count,
            "interval": self.interval,
            "max_retries": self.max_retries,
            "available_tools": self._get_available_tools(),
            "event_router": self.get_event_store_info(),
            "memory_router": self.memory_router.get_memory_store_info()
            if hasattr(self.memory_router, "get_memory_store_info")
            else {"type": "default"},
            "event_stream_info": self.get_event_stream_info(),
            "has_task": self.has_task(),
            "current_task_query": self.get_task_query() if self.has_task() else None,
        }

    def _get_available_tools(self) -> Dict[str, Any]:
        """Get information about available tools."""
        tools_info = {"mcp_tools": [], "local_tools": []}

        # Get MCP tools info
        if self.mcp_client and self.mcp_client.available_tools:
            tools_info["mcp_tools"] = list(self.mcp_client.available_tools.keys())

        # Get local tools info
        if self.local_tools:
            tools_info["local_tools"] = self.local_tools.list_tools()

        return tools_info

    async def update_config(self, new_config: Dict[str, Any]):
        """Update agent configuration."""
        try:
            # Update basic config
            if "interval" in new_config:
                self.interval = new_config["interval"]
            if "max_retries" in new_config:
                self.max_retries = new_config["max_retries"]
            if "retry_delay" in new_config:
                self.retry_delay = new_config["retry_delay"]

            logger.info(f"Updated configuration for agent {self.agent_id}")

        except Exception as e:
            logger.error(
                f"Failed to update configuration for agent {self.agent_id}: {e}"
            )
            raise

    async def cleanup(self):
        """Clean up background agent resources."""
        try:
            # Stop any running tasks
            if self.is_running:
                logger.info(f"Stopping running task for agent {self.agent_id}")
                # Note: This is a simple approach; in production you might want more sophisticated task cancellation

            # Clean up base agent
            await super().cleanup()

            logger.info(f"Cleaned up background agent {self.agent_id}")

        except Exception as e:
            logger.error(f"Failed to cleanup background agent {self.agent_id}: {e}")
            raise
