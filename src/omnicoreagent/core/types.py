from enum import Enum


class ContextInclusion(str, Enum):
    NONE = "none"
    THIS_SERVER = "thisServer"
    ALL_SERVERS = "allServers"


class AgentState(str, Enum):
    IDLE = "idle"
    RUNNING = "running"
    TOOL_CALLING = "tool_calling"
    OBSERVING = "observing"
    FINISHED = "finished"
    ERROR = "error"
    STUCK = "stuck"
