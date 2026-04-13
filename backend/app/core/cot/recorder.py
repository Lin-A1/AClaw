"""Chain of Thought 记录器"""
import time
import json
import os
from dataclasses import dataclass, field, asdict
from typing import Optional


@dataclass
class ThoughtStep:
    step: int
    content: str
    timestamp: float = field(default_factory=time.time)
    tool_name: Optional[str] = None
    token_usage: dict = field(default_factory=dict)


class COTRecorder:
    """思维链记录器"""

    def __init__(self, session_id: str, cot_dir: str):
        self._session_id = session_id
        self._dir = cot_dir
        self._steps: list[ThoughtStep] = []
        self._step_count = 0
        os.makedirs(self._dir, exist_ok=True)

    def record(
        self,
        content: str,
        tool_name: Optional[str] = None,
        token_usage: Optional[dict] = None,
    ) -> None:
        self._step_count += 1
        self._steps.append(
            ThoughtStep(
                step=self._step_count,
                content=content,
                tool_name=tool_name,
                token_usage=token_usage or {},
            )
        )

    def get_steps(self) -> list[ThoughtStep]:
        return list(self._steps)

    def get_summary(self) -> str:
        lines = []
        for s in self._steps:
            tool_info = f" [tool: {s.tool_name}]" if s.tool_name else ""
            lines.append(f"**Step {s.step}**{tool_info}\n{s.content}")
        return "\n\n---\n\n".join(lines)

    async def save(self) -> None:
        path = os.path.join(self._dir, f"{self._session_id}_cot.json")
        data = [asdict(s) for s in self._steps]
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def clear(self) -> None:
        self._steps.clear()
        self._step_count = 0
