"""
内置工具集。
每个工具使用 LangChain @tool 装饰器定义。
"""

from agent.tools.bash import bash
from agent.tools.config import config
from agent.tools.file_edit import file_edit
from agent.tools.file_read import file_read
from agent.tools.file_write import file_write
from agent.tools.glob import glob
from agent.tools.grep import grep
from agent.tools.todo_write import todo_write

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
