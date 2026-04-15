"""
内置工具集。
每个工具使用 LangChain @tool 装饰器定义。
"""

from claw.tools.bash import bash
from claw.tools.config import config
from claw.tools.file_edit import file_edit
from claw.tools.file_read import file_read
from claw.tools.file_write import file_write
from claw.tools.glob import glob
from claw.tools.grep import grep
from claw.tools.todo_write import todo_write

# 全部内置工具列表，注入到 Agent 时直接传入
ALL_TOOLS = [
    bash,
    file_read,
    file_write,
    file_edit,
    glob,
    grep,
    todo_write,
    config,
]

__all__ = [
    "bash",
    "file_read",
    "file_write",
    "file_edit",
    "glob",
    "grep",
    "todo_write",
    "config",
    "ALL_TOOLS",
]
