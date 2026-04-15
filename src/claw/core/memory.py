"""
Memory — 长期记忆 + 用户画像 + 会话历史。

使用方式：
    from claw.core.memory import memory

    memory.userprofile.user_info      # str，user.md 内容
    memory.userprofile.preferences   # str，preferences.md 内容
    memory.longterm.longterm_dir    # str
    memory.shortterm               # str（占位）
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import BaseModel, Field


_ROOT: Path = Path(__file__).parent.parent.parent.parent
_MEMORY_DIR: Path = _ROOT / ".claw" / "memory"
_LONGTERM_DIR: Path = _MEMORY_DIR / "longterm"


class UserProfile(BaseModel):
    """用户画像。"""

    user_info: str = ""
    preferences: str = ""
    user_info_path: str = ""
    preferences_path: str = ""


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
            user_info=user_info_content,
            preferences=preferences_content,
            user_info_path=str(user_info_path),
            preferences_path=str(preferences_path),
        )
    )


# 模块级单例，模块加载时从文件读取
memory: Memory = _get_memory()
