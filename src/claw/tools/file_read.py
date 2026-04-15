"""
FileRead — 读取文件内容，支持行范围分页。
"""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

from langchain_core.tools import tool
from pydantic import BaseModel, Field


class FileReadInput(BaseModel):
    path: Annotated[str, Field(description="文件路径")]
    offset: Annotated[int, Field(default=1, description="起始行号（1-based）")] = 1
    limit: Annotated[int, Field(default=200, description="最多读取行数")] = 200


@tool(args_schema=FileReadInput)
def file_read(path: str, offset: int = 1, limit: int = 200) -> str:
    """
    读取文件指定行范围。

    - offset: 起始行（1-based），默认第 1 行
    - limit: 最多读取行数，默认 200 行
    """
    p = Path(path)
    if not p.exists():
        return f"[错误] 文件不存在: {path}"
    if not p.is_file():
        return f"[错误] 不是普通文件: {path}"

    try:
        lines = p.read_text(encoding="utf-8").splitlines()
    except Exception as exc:
        return f"[错误] 无法读取: {exc}"

    start = max(0, offset - 1)
    end = min(len(lines), start + limit)
    content = "\n".join(f"{i + 1:>6}: {lines[i]}" for i in range(start, end))
    info = f"--- {path} (行 {offset}-{end}/{len(lines)}) ---"
    return f"{info}\n{content}"
