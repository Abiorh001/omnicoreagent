from __future__ import annotations

import time
import uuid
from typing import Any, Optional, Set

from pydantic import BaseModel, Field

from ..session._session_util import EventContent, GroundingMetadata


class EventActions(BaseModel):
    """Actions associated with an event."""

    state_delta: Optional[dict[str, Any]] = None
    """Changes to the session state."""

    function_calls: Optional[list[dict[str, Any]]] = None
    """Function or tool calls made."""

    observations: Optional[list[str]] = None
    """Observations or results from actions."""


class Event(BaseModel):
    """Represents an event in a session.

    Events capture interactions between users, agents, and tools.
    """

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    """Unique identifier for the event."""

    invocation_id: str
    """Identifier for the invocation that created this event."""

    author: str
    """Author of the event (user, assistant, tool, etc.)."""

    branch: Optional[str] = None
    """Branch identifier for conversation branching."""

    timestamp: float = Field(default_factory=time.time)
    """Unix timestamp when the event was created."""

    content: Optional[EventContent] = None
    """The content/payload of the event."""

    actions: Optional[EventActions] = None
    """Actions performed as part of this event."""

    long_running_tool_ids: Set[str] = Field(default_factory=set)
    """Set of tool IDs for long-running operations."""

    grounding_metadata: Optional[GroundingMetadata] = None
    """Metadata for grounding information."""

    partial: Optional[bool] = None
    """Whether this is a partial event."""

    turn_complete: Optional[bool] = None
    """Whether this event completes a turn."""

    error_code: Optional[str] = None
    """Error code if the event represents an error."""

    error_message: Optional[str] = None
    """Error message if the event represents an error."""

    interrupted: Optional[bool] = None
    """Whether the event was interrupted."""

    def __repr__(self) -> str:
        return f"<Event(id={self.id[:8]}..., author={self.author}, timestamp={self.timestamp})>"
