"""
Memory — 长期记忆 + 会话历史。

使用方式：
    from claw.core.memory import memory

    memory.longterm.user_info       # str，从 user.md 读取
    memory.longterm.preferences     # str，从 preferences.md 读取
    memory.longterm.longterm_dir    # Path str，不读取内容
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import BaseModel, Field

_ROOT: Path = Path(__file__).parent.parent.parent.parent
_LONGTERM_DIR: Path = _ROOT / ".claw" / "memory" / "longterm"


def _read_md(filename: str) -> str:
    """读取 memory 目录下的 .md 文件内容。"""
    path = _ROOT / ".claw" / "memory" / filename
    if path.exists():
        return path.read_text(encoding="utf-8").strip()
    return ""


class LongTermMemory(BaseModel):
    """长期记忆，包含 user_info、preferences、longterm_dir（路径，不读内容）。"""

    user_info: str = ""
    preferences: str = ""
    longterm_dir: str = str(_LONGTERM_DIR)


class Memory(BaseModel):
    """聚合各类记忆，预留短期记忆字段。"""

    longterm: LongTermMemory = Field(default_factory=LongTermMemory)
    shortterm: str = ""  # 占位
    session: str = ""  # 占位


@lru_cache(maxsize=1)
def _get_memory() -> Memory:
    return Memory(
        longterm=LongTermMemory(
            user_info=_read_md("user.md"),
            preferences=_read_md("preferences.md"),
            longterm_dir=str(_LONGTERM_DIR),
        )
    )


# 模块级单例，模块加载时从文件读取
memory: Memory = _get_memory()
