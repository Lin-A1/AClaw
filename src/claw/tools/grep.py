"""
Grep — 正则表达式内容搜索。
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Annotated

from langchain_core.tools import tool
from pydantic import BaseModel, Field

from claw.utils.logger import logger


class GrepInput(BaseModel):
    pattern: Annotated[str, Field(description="正则表达式")]
    path: Annotated[str | None, Field(default=None, description="搜索路径，None 则搜索当前目录")] = None
    file_pattern: Annotated[str | None, Field(default=None, description="限定文件类型，如 *.py、*.txt")] = None
    case_sensitive: Annotated[bool, Field(default=False, description="是否大小写敏感")] = False


@tool(args_schema=GrepInput)
def grep(
    pattern: str,
    path: str | None = None,
    file_pattern: str | None = None,
    case_sensitive: bool = False,
) -> str:
    """
    在文件内容中搜索正则表达式，返回匹配行及行号。

    - pattern: 正则表达式
    - path: 搜索目录，None 则当前目录
    - file_pattern: 限定文件类型，如 "*.py"
    - case_sensitive: 是否大小写敏感，默认 False
    """
    search_root = Path(path) if path else Path.cwd()

    if not search_root.exists():
        return f"[错误] 路径不存在: {search_root}"

    flags = 0 if case_sensitive else re.IGNORECASE
    try:
        compiled = re.compile(pattern, flags)
    except re.error as exc:
        return f"[错误] 正则表达式无效: {exc}"

    try:
        glob_pat = f"**/{file_pattern}" if file_pattern else "**/*"
        files = [p for p in search_root.glob(glob_pat) if p.is_file()]
    except Exception as exc:
        logger.error(f"grep 文件遍历失败 [{search_root}]: {exc}")
        return f"[错误] 文件遍历失败: {exc}"

    results: list[str] = []
    for fpath in sorted(files):
        try:
            lines = fpath.read_text(encoding="utf-8").splitlines()
        except Exception:
            continue
        for i, line in enumerate(lines, 1):
            if compiled.search(line):
                results.append(f"{fpath}:{i}: {line.rstrip()}")

    if not results:
        return "[无匹配]"
    return "\n".join(results)
