from typing import Any, Optional, Dict
from pydantic import BaseModel


class EventContent(BaseModel):
    """Base class for event content."""

    pass


class UserContent(EventContent):
    """Content for user message."""

    text: Optional[str] = None


class AssistantContent(EventContent):
    """Content for assistant message."""

    text: Optional[str] = None


class ToolContent(EventContent):
    """Content for tool call response."""

    tool_name: Optional[str] = None
    tool_input: Optional[Dict[str, Any]] = None
    tool_output: Optional[Any] = None


class GroundingMetadata(BaseModel):
    """Metadata for grouding information."""

    source: Optional[list[str]] = None
    confidence: Optional[float] = None
    citation: Optional[list[Dict[str, Any]]] = None


def decode_content(content_data: Optional[Dict[str, Any]]) -> Optional[EventContent]:
    """Decode content data into appropriate EventContent subclass.

    Args:
        content_data: Raw content data from storage

    Returns:
        Decoded EventContent object or None
    """

    if not content_data:
        return None

    content_type = content_data.get("type", "user")

    # Create a copy of content_data without the "type" field
    content_data_clean = {k: v for k, v in content_data.items() if k != "type"}

    if content_type == "user":
        return UserContent(**content_data_clean)
    elif content_type == "assistant":
        return AssistantContent(**content_data_clean)
    elif content_type == "tool":
        return ToolContent(**content_data_clean)
    else:
        return EventContent(**content_data_clean)


def decode_grounding_metadata(
    metadata_data: Optional[Dict[str, Any]],
) -> Optional[GroundingMetadata]:
    """Decode grounding metadata from storage.

    Args:
        metadata_data: Raw grounding metadata from storage

    Returns:
        Decoded GroundingMetadata object or None
    """
    if not metadata_data:
        return None

    return GroundingMetadata(**metadata_data)
