from mcpomni_connect.events.base import BaseEventStore
from mcpomni_connect.events.in_memory import InMemoryEventStore
from mcpomni_connect.events.redis_stream import RedisStreamEventStore
from mcpomni_connect.utils import logger
import os
from decouple import config

EVENT_BACKEND = config("EVENT_BACKEND", default="memory")
if EVENT_BACKEND == "redis_stream":
    logger.info("Using RedisStreamEventStore")
    event_store = RedisStreamEventStore()
else:
    logger.info("Using InMemoryEventStore")
    event_store = InMemoryEventStore()
