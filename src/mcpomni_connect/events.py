import asyncio
from collections import defaultdict
from typing import AsyncIterator, Any, Dict, List, Optional, Union
from enum import Enum
from datetime import datetime
from uuid import uuid4
from typing import Type
from pydantic import BaseModel, Field
from mcpomni_connect.utils import logger
class EventType(str, Enum):
    USER_MESSAGE = "user_message"
    AGENT_MESSAGE = "agent_message"
    TOOL_CALL_STARTED = "tool_call_started"
    TOOL_CALL_RESULT = "tool_call_result"
    TOOL_CALL_ERROR = "tool_call_error"
    FINAL_ANSWER = "final_answer"

class UserMessagePayload(BaseModel):
    message: str

class AgentMessagePayload(BaseModel):
    message: str

class ToolCallStartedPayload(BaseModel):
    tool_name: str
    tool_args: Dict[str, Any]
    tool_call_id: Optional[str] = None

class ToolCallResultPayload(BaseModel):
    tool_name: str
    tool_args: Dict[str, Any]
    tool_call_id: Optional[str] = None
    result: str

class ToolCallErrorPayload(BaseModel):
    tool_name: str
    error_message: str

class FinalAnswerPayload(BaseModel):
    message: str
    confidence: Optional[float] = None
    sources: Optional[List[str]] = None


EventPayload = Union[
    UserMessagePayload,
    AgentMessagePayload,
    ToolCallStartedPayload,
    ToolCallResultPayload,
    ToolCallErrorPayload,
    FinalAnswerPayload,
    
]

class Event(BaseModel):
    type: EventType
    payload: EventPayload
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    agent_name: str
    event_id: str = Field(default_factory=lambda: str(uuid4()))


EVENT_PAYLOAD_MAP: dict[EventType, Type[BaseModel]] = {
    EventType.USER_MESSAGE: UserMessagePayload,
    EventType.AGENT_MESSAGE: AgentMessagePayload,
    EventType.TOOL_CALL_STARTED: ToolCallStartedPayload,
    EventType.TOOL_CALL_RESULT: ToolCallResultPayload,
    EventType.TOOL_CALL_ERROR: ToolCallErrorPayload,
    EventType.FINAL_ANSWER: FinalAnswerPayload,
}

def validate_event(event: Event):
    expected_type = EVENT_PAYLOAD_MAP[event.type]
    if not isinstance(event.payload, expected_type):
        raise TypeError(f"Payload mismatch: Expected {expected_type} for {event.type}, got {type(event.payload)}")

class EventStore:
    def __init__(self):
        self.logs: dict[str, list[Event]] = defaultdict(list)
        self.queues: dict[str, asyncio.Queue] = defaultdict(asyncio.Queue)

    def append(self, session_id: str, event: Event):
        validate_event(event)
        self.logs[session_id].append(event)
        self.queues[session_id].put_nowait(event)
        

    def get_events(self, session_id: str) -> list[Event]:
        return self.logs[session_id]

    async def stream(self, session_id: str) -> AsyncIterator[Event]:
        queue = self.queues[session_id]
        while True:
            event = await queue.get()
            yield event

event_store = EventStore()