"""
Memory — 长期记忆 + 用户画像 + 会话历史。

使用方式：
    from claw.core.memory import memory

    memory.userprofile.user_info          # 读取用户信息
    memory.userprofile.save_user_info()   # 写回 user.md

    memory.longterm.list_files()          # 列出所有长期记忆文件名
    memory.longterm.read("work.md")       # 读取某个文件
    memory.longterm.write("work.md", ...) # 写入/覆盖某个文件
    memory.longterm.append("work.md", ...) # 追加内容
    memory.longterm.delete("work.md")     # 删除某个文件
"""

from __future__ import annotations

import os
from pathlib import Path

from pydantic import BaseModel, Field

_MEMORY_DIR: Path = Path(
    os.environ.get("CLAW_MEMORY_DIR", Path.home() / ".claw" / "memory")
)
_LONGTERM_DIR: Path = _MEMORY_DIR / "longterm"


class UserProfile(BaseModel):
    """用户画像，对应 memory/user.md 和 memory/preferences.md。"""

    model_config = {"arbitrary_types_allowed": True}

    _user_info_path: Path = _MEMORY_DIR / "user.md"
    _preferences_path: Path = _MEMORY_DIR / "preferences.md"

    user_info: str = ""
    preferences: str = ""

    def reload(self) -> None:
        """从文件重新加载（运行期文件被修改后调用）。"""
        self.user_info = self._read(_MEMORY_DIR / "user.md")
        self.preferences = self._read(_MEMORY_DIR / "preferences.md")


    def save_user_info(self, content: str | None = None) -> None:
        """将 user_info 写回 user.md。content 不为 None 时同时更新字段。"""
        if content is not None:
            self.user_info = content
        self._write(_MEMORY_DIR / "user.md", self.user_info)

    def save_preferences(self, content: str | None = None) -> None:
        """将 preferences 写回 preferences.md。"""
        if content is not None:
            self.preferences = content
        self._write(_MEMORY_DIR / "preferences.md", self.preferences)


    @staticmethod
    def _read(path: Path) -> str:
        return path.read_text(encoding="utf-8").strip() if path.exists() else ""

    @staticmethod
    def _write(path: Path, content: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")


class LongTermMemory(BaseModel):
    """
    长期记忆目录管理。

    目录结构示例：
        .claw/memory/longterm/
            work.md
            projects.md
            contacts.md
            ...

    Agent 可通过工具调用 list_files / read / write / append / delete
    来管理这些文件。
    """

    model_config = {"arbitrary_types_allowed": True}

    _dir: Path = _LONGTERM_DIR

    @property
    def dir(self) -> Path:
        self._dir.mkdir(parents=True, exist_ok=True)
        return self._dir


    def list_files(self) -> list[str]:
        """返回目录下所有 .md 文件名（不含路径）。"""
        return sorted(p.name for p in self.dir.glob("*.md"))

    def read(self, filename: str) -> str:
        """读取指定文件内容，文件不存在时返回空字符串。"""
        path = self._resolve(filename)
        return path.read_text(encoding="utf-8").strip() if path.exists() else ""

    def exists(self, filename: str) -> bool:
        return self._resolve(filename).exists()


    def write(self, filename: str, content: str) -> None:
        """写入（覆盖）指定文件。"""
        path = self._resolve(filename)
        path.write_text(content, encoding="utf-8")

    def append(self, filename: str, content: str, separator: str = "\n\n") -> None:
        """向文件末尾追加内容，文件不存在时自动创建。"""
        existing = self.read(filename)
        new_content = (existing + separator + content).strip() if existing else content
        self.write(filename, new_content)

    def delete(self, filename: str) -> bool:
        """删除文件，返回是否成功（文件不存在返回 False）。"""
        path = self._resolve(filename)
        if path.exists():
            path.unlink()
            return True
        return False


    def _resolve(self, filename: str) -> Path:
        """将文件名解析为完整路径，并防止路径穿越。"""
        # 只允许文件名，不允许 ../../../etc/passwd 之类的路径
        name = Path(filename).name
        if not name.endswith(".md"):
            name = name + ".md"
        return self.dir / name


class Memory(BaseModel):
    """聚合各类记忆的顶层对象。"""

    model_config = {"arbitrary_types_allowed": True}

    userprofile: UserProfile = Field(default_factory=UserProfile)
    longterm: LongTermMemory = Field(default_factory=LongTermMemory)
    shortterm: str = ""  # 占位，后续对接 langgraph checkpointer


def _load_memory() -> Memory:
    """初始化并从文件读取用户画像。"""
    m = Memory()
    m.userprofile.reload()
    return m


# 模块级单例；需要刷新时调用 memory.userprofile.reload()
memory: Memory = _load_memory()
