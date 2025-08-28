"""
Event System Package

This package provides event handling and routing:
- BaseEventStore: Abstract base for event stores
- InMemoryEventStore: In-memory event storage
- RedisStreamEventStore: Redis stream-based events
- EventRouter: Routes events to appropriate handlers
"""

from .event_router import EventRouter

__all__ = [
    "EventRouter",
]
