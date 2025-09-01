import redis.asyncio as redis
from typing import AsyncIterator, List
from decouple import config
from omnicoreagent.core.events.base import BaseEventStore, Event

REDIS_URL = config("REDIS_URL", default="redis://localhost:6379/0")


class RedisStreamEventStore(BaseEventStore):
    def __init__(self):
        self.redis = redis.from_url(REDIS_URL, decode_responses=True)

    async def append(self, session_id: str, event: Event):
        stream_name = f"omnicoreagent_events:{session_id}"
        await self.redis.xadd(stream_name, {"event": event.json()})

    async def get_events(self, session_id: str) -> List[Event]:
        stream_name = f"omnicoreagent_events:{session_id}"
        events = await self.redis.xrange(stream_name, min="-", max="+")
        return [Event.parse_raw(entry[1]["event"]) for entry in events]

    async def stream(self, session_id: str) -> AsyncIterator[Event]:
        stream_name = f"omnicoreagent_events:{session_id}"
        last_id = "0-0"
        while True:
            results = await self.redis.xread({stream_name: last_id}, block=0, count=1)
            if results:
                _, entries = results[0]
                for entry_id, data in entries:
                    last_id = entry_id
                    yield Event.parse_raw(data["event"])
