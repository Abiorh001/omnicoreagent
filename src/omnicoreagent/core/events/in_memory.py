from collections import defaultdict
import asyncio
from typing import AsyncIterator
from omnicoreagent.core.events.base import BaseEventStore, Event


class InMemoryEventStore(BaseEventStore):
    def __init__(self):
        self.logs: dict[str, list[Event]] = defaultdict(list)
        self.queues: dict[str, asyncio.Queue] = defaultdict(asyncio.Queue)

    async def append(self, session_id: str, event: Event) -> None:
        self.logs[session_id].append(event)
        self.queues[session_id].put_nowait(event)

    async def get_events(self, session_id: str) -> list[Event]:
        return self.logs[session_id]

    async def stream(self, session_id: str) -> AsyncIterator[Event]:
        queue = self.queues[session_id]
        while True:
            event = await queue.get()
            yield event
