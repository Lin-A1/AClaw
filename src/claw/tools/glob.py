"""
Glob — 按模式匹配文件路径，类似 shell glob / find。
"""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

from langchain_core.tools import tool
from pydantic import BaseModel, Field


class GlobInput(BaseModel):
    pattern: Annotated[str, Field(description="glob 模式，如 **/*.py、src/**/*.ts")]
    root: Annotated[str | None, Field(default=None, description="搜索根目录，None 则用当前目录")] = None


@tool(args_schema=GlobInput)
def glob(pattern: str, root: str | None = None) -> str:
    """
    按 glob 模式搜索文件路径。

    示例：
      glob("**/*.py")           — 递归所有 .py 文件
      glob("src/**/*.ts")       — src 下所有 .ts 文件
      glob("*.txt")             — 当前目录 .txt 文件
    """
    root_path = Path(root) if root else Path.cwd()

    if ".." in pattern:
        return "[错误] 不允许使用 .. 路径穿越"

    try:
        matches = list(root_path.glob(pattern))
    except Exception as exc:
        return f"[错误] glob 失败: {exc}"

    if not matches:
        return "[无匹配]"

    relative = [str(p.relative_to(root_path)) for p in matches]
    relative.sort()
    return "\n".join(relative)
