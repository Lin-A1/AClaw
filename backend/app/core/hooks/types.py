"""Hook 事件类型和上下文"""
from enum import Enum
from dataclasses import dataclass, field
from typing import Any, Optional


class HookEvent(str, Enum):
    PRE_AGENT_RUN = "pre_agent_run"
    POST_AGENT_RUN = "post_agent_run"
    ON_AGENT_ERROR = "on_agent_error"
    PRE_TOOL_USE = "pre_tool_use"
    POST_TOOL_USE = "post_tool_use"
    PRE_MEMORY_FLUSH = "pre_memory_flush"
    POST_MEMORY_FLUSH = "post_memory_flush"
    PRE_COMPACT = "pre_compact"
    POST_COMPACT = "post_compact"


@dataclass
class HookContext:
    event: HookEvent
    session_id: str = ""
    tool_name: Optional[str] = None
    tool_input: Optional[dict] = None
    tool_output: Any = None
    agent_output: Any = None
    error: Optional[Exception] = None
    metadata: dict = field(default_factory=dict)
    blocked: bool = False
    block_reason: str = ""
