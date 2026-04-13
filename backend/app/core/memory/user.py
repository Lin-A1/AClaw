"""用户记忆 - 读写 user.md"""
import os


class UserMemory:
    """用户身份档案，持久存储"""

    def __init__(self, base_dir: str):
        self._path = os.path.join(base_dir, "user.md")

    def load(self) -> str:
        if not os.path.exists(self._path):
            return ""
        with open(self._path, "r", encoding="utf-8") as f:
            return f.read().strip()

    def save(self, content: str) -> None:
        with open(self._path, "w", encoding="utf-8") as f:
            f.write(content)
