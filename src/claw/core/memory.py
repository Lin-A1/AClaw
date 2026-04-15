"""
Memory — 长期记忆 + 用户画像 + 会话历史。

使用方式：
    from claw.core.memory import memory

    memory.userprofile.user_info.content    # str，user.md 内容
    memory.userprofile.user_info.path      # str，user.md 路径
    memory.userprofile.preferences.content # str，preferences.md 内容
    memory.userprofile.preferences.path    # str，preferences.md 路径
    memory.longterm.longterm_dir           # str
    memory.shortterm                       # str（占位）
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import BaseModel, Field

_ROOT: Path = Path(__file__).parent.parent.parent.parent
_MEMORY_DIR: Path = _ROOT / ".claw" / "memory"
_LONGTERM_DIR: Path = _MEMORY_DIR / "longterm"


class UserInfo(BaseModel):
    """用户信息：content=文件内容，path=文件路径。"""

    content: str = ""
    path: str = ""


class Preferences(BaseModel):
    """用户偏好：content=文件内容，path=文件路径。"""

    content: str = ""
    path: str = ""


class UserProfile(BaseModel):
    """用户画像。"""

    user_info: UserInfo
    preferences: Preferences


class LongTermMemory(BaseModel):
    """长期记忆。"""

    longterm_dir: str = str(_LONGTERM_DIR)


class Memory(BaseModel):
    """聚合各类记忆。"""

    userprofile: UserProfile = Field(default_factory=UserProfile)
    longterm: LongTermMemory = Field(default_factory=LongTermMemory)
    shortterm: str = ""  # 占位
    session: str = ""  # 占位


@lru_cache(maxsize=1)
def _get_memory() -> Memory:
    user_info_path = _MEMORY_DIR / "user.md"
    preferences_path = _MEMORY_DIR / "preferences.md"

    user_info_content = user_info_path.read_text(encoding="utf-8").strip() if user_info_path.exists() else ""
    preferences_content = preferences_path.read_text(encoding="utf-8").strip() if preferences_path.exists() else ""

    return Memory(
        userprofile=UserProfile(
            user_info=UserInfo(content=user_info_content, path=str(user_info_path)),
            preferences=Preferences(content=preferences_content, path=str(preferences_path)),
        )
    )


# 模块级单例，模块加载时从文件读取
memory: Memory = _get_memory()
