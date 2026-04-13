"""Edit tool: replace specific text in a file"""
import os
from pydantic import Field
from langchain_core.tools import BaseTool


class EditTool(BaseTool):
    """替换文件中指定的文本片段。适用于修改文件中的一部分内容而非全量覆写。"""
    name: str = "Edit"
    description: str = """替换文件中指定的文本片段。
接收 file_path（旧文本片段，新文本）三个参数。
旧文本必须是文件中唯一存在的精确字符串，否则会失败。
适用于修单行、修改代码、配置等场景。"""

    def _run(self, file_path: str, old_string: str, new_string: str) -> str:
        try:
            if not os.path.exists(file_path):
                return f"文件不存在: {file_path}"
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            if old_string not in content:
                return f"未找到要替换的文本: {repr(old_string[:50])}"
            new_content = content.replace(old_string, new_string, 1)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(new_content)
            return f"成功修改文件: {file_path}"
        except PermissionError:
            return f"权限不足，无法修改: {file_path}"
        except Exception as e:
            return f"修改文件 {file_path} 失败: {e}"
