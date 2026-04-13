"""Agent 运行上下文"""
from dataclasses import dataclass, field
from typing import Optional
from app.core.cot.recorder import COTRecorder


@dataclass
class AgentContext:
    session_id: str
    user_message: str
    language: str = "zh"
    system_prompt: str = ""
    cot: Optional[COTRecorder] = None
    metadata: dict = field(default_factory=dict)
