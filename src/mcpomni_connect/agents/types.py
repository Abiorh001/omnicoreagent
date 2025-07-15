# types.py
from enum import Enum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class AgentConfig(BaseModel):
    agent_name: str
    request_limit: int
    total_tokens_limit: int
    max_steps: int = Field(gt=0, le=1000)
    tool_call_timeout: int = Field(gt=1, le=1000)
    memory_config: dict = {"mode": "sliding_window", "value": 10000}


class AgentState(str, Enum):
    IDLE = "idle"
    RUNNING = "running"
    TOOL_CALLING = "tool_calling"
    OBSERVING = "observing"
    FINISHED = "finished"
    ERROR = "error"
    STUCK = "stuck"


class ToolFunction(BaseModel):
    name: str
    arguments: str


class ToolCall(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    type: str = "function"
    function: ToolFunction


class ToolCallMetadata(BaseModel):
    has_tool_calls: bool = False
    tool_calls: list[ToolCall] = []
    tool_call_id: UUID | None = None
    agent_name: str | None = None


class Message(BaseModel):
    role: str
    content: str
    tool_call_id: str = None
    tool_calls: str = None
    metadata: ToolCallMetadata | None = None


class ParsedResponse(BaseModel):
    action: bool | None = None
    data: str | None = None
    error: str | None = None
    answer: str | None = None


class ToolCallResult(BaseModel):
    tool_executor: Any  # ToolExecutor instance
    tool_name: str
    tool_args: dict


class ToolError(BaseModel):
    observation: str
    tool_name: str
    tool_args: dict | None = None


class ToolData(BaseModel):
    action: bool
    tool_name: str | None = None
    tool_args: dict | None = None
    error: str | None = None


class ToolCallRecord(BaseModel):
    tool_name: str
    tool_args: str
    observation: str


class ToolParameter(BaseModel):
    type: str
    description: str


class ToolRegistryEntry(BaseModel):
    name: str
    description: str
    parameters: list[ToolParameter] = []


class ToolExecutorConfig(BaseModel):
    handler: Any  # ToolExecutor instance
    tool_data: dict[str, Any]
    available_tools: dict[str, Any]


class LoopDetectorConfig(BaseModel):
    max_repeats: int = 3
    similarity_threshold: float = 0.9
