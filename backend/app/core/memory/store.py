"""记忆系统统一门面"""
from dataclasses import dataclass
from app.core.memory.user import UserMemory
from app.core.memory.preferences import PreferencesMemory
from app.core.memory.session import SessionMemory
from app.core.memory.longterm import LongtermMemory


@dataclass
class MemoryConfig:
    base_dir: str
    session_max_messages: int = 50
    flush_threshold: float = 0.8


class MemoryStore:
    """四层记忆统一管理"""

    def __init__(self, cfg: MemoryConfig):
        self.user = UserMemory(cfg.base_dir)
        self.preferences = PreferencesMemory(cfg.base_dir)
        self.session = SessionMemory(cfg.base_dir, cfg.session_max_messages)
        self.longterm = LongtermMemory(cfg.base_dir)
        self._cfg = cfg

    def build_system_context(self, session_id: str) -> str:
        """构建注入系统提示词的记忆块"""
        blocks = []
        if user := self.user.load():
            blocks.append(f"## User Profile\n{user}")
        if prefs := self.preferences.load():
            blocks.append(f"## Preferences\n{prefs}")
        if facts := self.longterm.load_facts():
            blocks.append(f"## Long-term Memory\n{facts}")
        return "\n\n".join(blocks)

    def get_history(self, session_id: str) -> list[dict]:
        return self.session.get_messages(session_id)

    def add_message(self, session_id: str, role: str, content: str) -> None:
        self.session.append(session_id, role, content)
