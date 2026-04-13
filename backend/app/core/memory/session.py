"""短期会话记忆 - 读写 session/*.json"""
import json
import os
import time
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Message:
    role: str
    content: str
    timestamp: float = field(default_factory=time.time)
    tool_name: Optional[str] = None


class SessionMemory:
    """短期会话记忆，会话内有效"""

    def __init__(self, base_dir: str, max_messages: int = 50):
        self._dir = os.path.join(base_dir, "session")
        self._max = max_messages
        os.makedirs(self._dir, exist_ok=True)

    def _path(self, session_id: str) -> str:
        return os.path.join(self._dir, f"{session_id}.json")

    def get_messages(self, session_id: str) -> list[dict]:
        path = self._path(session_id)
        if not os.path.exists(path):
            return []
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def append(
        self, session_id: str, role: str, content: str, tool_name: Optional[str] = None
    ) -> None:
        msgs = self.get_messages(session_id)
        msgs.append(
            {
                "role": role,
                "content": content,
                "timestamp": time.time(),
                "tool_name": tool_name,
            }
        )
        if len(msgs) > self._max:
            msgs = msgs[-self._max :]
        with open(self._path(session_id), "w", encoding="utf-8") as f:
            json.dump(msgs, f, ensure_ascii=False, indent=2)

    def clear(self, session_id: str) -> None:
        path = self._path(session_id)
        if os.path.exists(path):
            os.remove(path)

    def list_sessions(self) -> list[str]:
        return [f.removesuffix(".json") for f in os.listdir(self._dir) if f.endswith(".json")]
