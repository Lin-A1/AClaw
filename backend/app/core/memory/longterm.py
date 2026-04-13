"""长期记忆 - 读写 longterm/*.md"""
import os
from datetime import datetime


class LongtermMemory:
    """长期记忆提炼，跨会话持久"""

    def __init__(self, base_dir: str):
        self._dir = os.path.join(base_dir, "longterm")
        os.makedirs(self._dir, exist_ok=True)
        self._facts_path = os.path.join(self._dir, "facts.md")

    def load_facts(self) -> str:
        if not os.path.exists(self._facts_path):
            return ""
        with open(self._facts_path, "r", encoding="utf-8") as f:
            return f.read().strip()

    def append_facts(self, facts: str) -> None:
        ts = datetime.now().strftime("%Y-%m-%d %H:%M")
        entry = f"\n\n### {ts}\n{facts.strip()}"
        with open(self._facts_path, "a", encoding="utf-8") as f:
            f.write(entry)

    def save_project(self, name: str, content: str) -> None:
        path = os.path.join(self._dir, f"{name}.md")
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

    def load_project(self, name: str) -> str:
        path = os.path.join(self._dir, f"{name}.md")
        if not os.path.exists(path):
            return ""
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
