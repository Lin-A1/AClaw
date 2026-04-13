"""用户偏好 - 读写 preferences.md"""
import os


class PreferencesMemory:
    """用户偏好设置，持久存储"""

    def __init__(self, base_dir: str):
        self._path = os.path.join(base_dir, "preferences.md")

    def load(self) -> str:
        if not os.path.exists(self._path):
            return ""
        with open(self._path, "r", encoding="utf-8") as f:
            return f.read().strip()

    def save(self, content: str) -> None:
        with open(self._path, "w", encoding="utf-8") as f:
            f.write(content)
