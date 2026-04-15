"""
FileWrite — 写入文件（覆盖），自动创建父目录。
"""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

from langchain_core.tools import tool
from pydantic import BaseModel, Field


class FileWriteInput(BaseModel):
    path: Annotated[str, Field(description="文件路径")]
    content: Annotated[str, Field(description="文件内容（会覆盖已有内容）")]


@tool(args_schema=FileWriteInput)
def file_write(path: str, content: str) -> str:
    """
    将 content 写入 path，覆盖已有内容。
    父目录不存在时自动创建。
    """
    p = Path(path)
    try:
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        return f"[写入成功] {path} ({len(content)} bytes)"
    except Exception as exc:
        return f"[错误] 写入失败: {exc}"
