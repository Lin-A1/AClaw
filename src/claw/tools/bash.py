"""
Bash — 执行 Shell 命令。
"""

from __future__ import annotations

import subprocess
from typing import Annotated

from langchain_core.tools import tool
from pydantic import BaseModel, Field


class BashInput(BaseModel):
    command: Annotated[str, Field(description="要执行的 shell 命令")]
    timeout: Annotated[int, Field(default=30, description="超时秒数")] = 30
    cwd: Annotated[str | None, Field(default=None, description="工作目录，None 则用当前目录")] = None


@tool(args_schema=BashInput)
def bash(command: str, timeout: int = 30, cwd: str | None = None) -> str:
    """执行一条 shell 命令，返回 stdout + stderr 合并结果。"""
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=cwd,
        )
        output = result.stdout + result.stderr
        if result.returncode == 0:
            return output or "(命令执行成功，无输出)"
        return f"[exit {result.returncode}]\n{output}"
    except subprocess.TimeoutExpired:
        return f"[超时 {timeout}s]"
    except Exception as exc:
        return f"[错误] {exc}"
