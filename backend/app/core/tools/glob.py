"""Glob tool: find files by pattern"""
import os
import glob as glob_lib
from pydantic import Field
from langchain_core.tools import BaseTool


class GlobTool(BaseTool):
    """根据 glob 模式查找文件路径。"""
    name: str = "Glob"
    description: str = """根据 glob 模式查找文件路径。
pattern 参数支持标准 glob 语法，如 "**/*.py"、"src/**/*.ts"、"*.md" 等。
root 参数可选，指定搜索根目录（默认当前目录）。
返回匹配文件的绝对路径列表，每行一个。"""

    def _run(self, pattern: str, root: str = ".") -> str:
        try:
            # 安全检查：禁止访问上级目录
            root = os.path.abspath(root)
            matches = glob_lib.glob(pattern, root_dir=root, recursive=True)
            if not matches:
                return f"未找到匹配模式 '{pattern}' 的文件"
            return "\n".join(os.path.abspath(os.path.join(root, m)) for m in matches)
        except Exception as e:
            return f"Glob 搜索失败: {e}"
