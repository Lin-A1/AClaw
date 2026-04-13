"""Agent 输出模型"""
from dataclasses import dataclass, field
from typing import Optional
from app.core.cot.recorder import ThoughtStep


@dataclass
class AgentOutput:
    response: str
    session_id: str
    thought_steps: list[ThoughtStep] = field(default_factory=list)
    tool_calls: list[dict] = field(default_factory=list)
    finish_reason: str = "stop"
    error: Optional[str] = None


@dataclass
class AgentChunk:
    """流式输出块"""
    type: str
    content: str = ""
    tool_name: Optional[str] = None
    session_id: str = ""
