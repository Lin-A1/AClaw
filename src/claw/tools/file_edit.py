"""
FileEdit — 精确字符串替换（old → new），每次只替换一处。
"""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

from langchain_core.tools import tool
from pydantic import BaseModel, Field


class FileEditInput(BaseModel):
    path: Annotated[str, Field(description="文件路径")]
    old_string: Annotated[str, Field(description="待替换的原字符串（必须精确匹配）")]
    new_string: Annotated[str, Field(description="替换后的新字符串")]


@tool(args_schema=FileEditInput)
def file_edit(path: str, old_string: str, new_string: str) -> str:
    """
    精确替换文件中的第一处 old_string 为 new_string。

    old_string 必须精确匹配（包括空白字符）。
    替换成功返回新文件内容摘要，失败返回错误原因。
    """
    p = Path(path)
    if not p.exists() or not p.is_file():
        return f"[错误] 文件不存在或不是普通文件: {path}"

    try:
        text = p.read_text(encoding="utf-8")
    except Exception as exc:
        return f"[错误] 读取失败: {exc}"

    if old_string not in text:
        return "[错误] old_string 未在文件中找到，请确认内容完全一致"

    new_text = text.replace(old_string, new_string, 1)
    p.write_text(new_text, encoding="utf-8")

    old_lines = text.count("\n") + 1
    new_lines = new_text.count("\n") + 1
    return (
        f"[替换成功] {path}\n"
        f"  old: {old_string[:80]!r}"
        + ("" if len(old_string) <= 80 else " ...")
        + f"\n  new: {new_string[:80]!r}"
        + ("" if len(new_string) <= 80 else " ...")
        + f"\n  行数变化: {old_lines} → {new_lines}"
    )
