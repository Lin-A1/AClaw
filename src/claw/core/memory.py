"""
Memory — 长期记忆 + 会话历史。

使用方式：
    from claw.core.memory import memory

    memory.longterm.user_info.content       # str，user.md 内容
    memory.longterm.user_info.path          # str，user.md 路径
    memory.longterm.preferences.content     # str，preferences.md 内容
    memory.longterm.preferences.path        # str，preferences.md 路径
    memory.longterm.longterm_dir            # str，不读取内容
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import BaseModel, Field

_ROOT: Path = Path(__file__).parent.parent.parent.parent
_MEMORY_DIR: Path = _ROOT / ".claw" / "memory"
_LONGTERM_DIR: Path = _MEMORY_DIR / "longterm"


class UserProfile(BaseModel):
    """用户画像：content=文件内容，path=文件路径。"""

    content: str = ""
    path: str = ""


class LongTermMemory(BaseModel):
    """长期记忆。"""

    user_info: UserProfile
    preferences: UserProfile
    longterm_dir: str = ""


class Memory(BaseModel):
    """聚合各类记忆，预留短期记忆字段。"""

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
        longterm=LongTermMemory(
            user_info=UserProfile(content=user_info_content, path=str(user_info_path)),
            preferences=UserProfile(content=preferences_content, path=str(preferences_path)),
            longterm_dir=str(_LONGTERM_DIR),
        )
    )


# 模块级单例，模块加载时从文件读取
memory: Memory = _get_memory()
