"""Write tool: write content to file"""
import os
from pydantic import Field
from langchain_core.tools import BaseTool


class WriteTool(BaseTool):
    """创建新文件或覆盖已有文件，写入指定内容。"""
    name: str = "Write"
    description: str = """创建新文件或覆盖已有文件，写入指定内容。
适用于创建新文件或完整覆写已有文件。
如果只需要修改部分内容，请使用 Edit 工具。"""

    def _run(self, file_path: str, content: str) -> str:
        try:
            # 确保父目录存在
            parent = os.path.dirname(file_path)
            if parent:
                os.makedirs(parent, exist_ok=True)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            return f"成功写入文件: {file_path} ({len(content)} 字符)"
        except PermissionError:
            return f"权限不足，无法写入: {file_path}"
        except Exception as e:
            return f"写入文件 {file_path} 失败: {e}"
