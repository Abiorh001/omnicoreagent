"""
Task registry for managing background agent task definitions.
"""

from typing import Dict, List, Optional
from omnicoreagent.core.utils import logger


class TaskRegistry:
    """Registry for storing and managing task definitions."""

    def __init__(self):
        self._tasks: Dict[str, Dict] = {}  # Replace with SQLite/Redis later

    def register(self, agent_id: str, config: Dict):
        """Register a new task configuration."""
        try:
            self._tasks[agent_id] = config
            logger.info(f"Registered task for agent: {agent_id}")
        except Exception as e:
            logger.error(f"Failed to register task for agent {agent_id}: {e}")
            raise

    def get(self, agent_id: str) -> Optional[Dict]:
        """Get task configuration for an agent."""
        return self._tasks.get(agent_id)

    def all_tasks(self) -> List[Dict]:
        """Get all registered task configurations."""
        return list(self._tasks.values())

    def remove(self, agent_id: str):
        """Remove a task configuration."""
        try:
            if agent_id in self._tasks:
                del self._tasks[agent_id]
                logger.info(f"Removed task for agent: {agent_id}")
        except Exception as e:
            logger.error(f"Failed to remove task for agent {agent_id}: {e}")
            raise

    def exists(self, agent_id: str) -> bool:
        """Check if a task exists for the given agent ID."""
        return agent_id in self._tasks

    def update(self, agent_id: str, config: Dict):
        """Update an existing task configuration."""
        if agent_id in self._tasks:
            self._tasks[agent_id].update(config)
            logger.info(f"Updated task for agent: {agent_id}")
        else:
            raise KeyError(f"Task for agent {agent_id} not found")

    def get_agent_ids(self) -> List[str]:
        """Get all registered agent IDs."""
        return list(self._tasks.keys())

    def clear(self):
        """Clear all registered tasks."""
        self._tasks.clear()
        logger.info("Cleared all registered tasks")
