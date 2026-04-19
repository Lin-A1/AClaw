"""
Memory — 多用户长期记忆 + 用户画像 + 会话历史。

目录结构（可通过 CLAW_MEMORY_DIR 环境变量覆盖）：
    .claw/memory/
    ├── users/
    │   └── {user_id}/                  # 多用户隔离
    │       ├── user.md                 # 用户画像
    │       ├── preferences.md          # 用户偏好
    │       └── longterm/               # 长期记忆文件
    └── session.db                      # 会话历史（由外部管理）

使用方式：
    from claw.core.memory import Memory

    # 访问默认用户（user_id="default"）
    memory = Memory()

    # 访问指定用户
    memory = Memory(user_id="alice")

    memory.userprofile.user_info         # 读取用户信息
    memory.userprofile.save_user_info()  # 写回 user.md

    memory.longterm.list_files()         # 列出所有长期记忆文件名
    memory.longterm.read("work.md")      # 读取某个文件
    memory.longterm.write("work.md", ...)  # 写入/覆盖某个文件
    memory.longterm.append("work.md", ...) # 追加内容
    memory.longterm.delete("work.md")    # 删除某个文件
"""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel

from claw.config.settings import settings
from claw.utils.logger import logger

_CLAW_MEMORY_DIR: Path = settings.memory.root
_USERS_DIR: Path = _CLAW_MEMORY_DIR / "users"


def _user_dir(user_id: str) -> Path:
    return _USERS_DIR / user_id


class UserProfile(BaseModel):
    """用户画像，对应 users/{user_id}/user.md 和 preferences.md。"""

    model_config = {"arbitrary_types_allowed": True}

    user_id: str = "default"
    user_info: str = ""
    preferences: str = ""

    def reload(self) -> None:
        """从文件重新加载（运行期文件被修改后调用）。"""
        user_dir = _user_dir(self.user_id)
        self.user_info = self._read(user_dir / "user.md")
        self.preferences = self._read(user_dir / "preferences.md")

    def save_user_info(self, content: str | None = None) -> None:
        """将 user_info 写回 user.md。content 不为 None 时同时更新字段。"""
        if content is not None:
            self.user_info = content
        self._write(_user_dir(self.user_id) / "user.md", self.user_info)

    def save_preferences(self, content: str | None = None) -> None:
        """将 preferences 写回 preferences.md。"""
        if content is not None:
            self.preferences = content
        self._write(_user_dir(self.user_id) / "preferences.md", self.preferences)

    @staticmethod
    def _read(path: Path) -> str:
        return path.read_text(encoding="utf-8").strip() if path.exists() else ""

    @staticmethod
    def _write(path: Path, content: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        try:
            path.write_text(content, encoding="utf-8")
        except Exception as e:
            logger.error(f"写入记忆文件失败 [{path}]: {e}")
            raise


class LongTermMemory(BaseModel):
    """
    长期记忆目录管理。

    目录结构示例：
        .claw/memory/users/{user_id}/longterm/
            work.md
            projects.md
            contacts.md
            ...

    Agent 可通过工具调用 list_files / read / write / append / delete
    来管理这些文件。
    """

    model_config = {"arbitrary_types_allowed": True}

    user_id: str = "default"

    @property
    def dir(self) -> Path:
        longterm_dir = _user_dir(self.user_id) / "longterm"
        longterm_dir.mkdir(parents=True, exist_ok=True)
        return longterm_dir


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

    user_id: str = "default"
    userprofile: UserProfile = UserProfile(user_id="default")
    longterm: LongTermMemory = LongTermMemory(user_id="default")
    shortterm: str = ""  # 占位，后续对接 langgraph checkpointer

    def __init__(self, user_id: str = "default", **kwargs):
        super().__init__(**kwargs)
        self.user_id = user_id
        self.userprofile = UserProfile(user_id=user_id)
        self.longterm = LongTermMemory(user_id=user_id)
        self.userprofile.reload()
