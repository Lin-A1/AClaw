"""Read tool: read file content"""
from typing import Optional
from pydantic import Field
from langchain_core.tools import BaseTool


class ReadTool(BaseTool):
    """读取文件的全部内容。适用于读取任何类型的文件（代码、配置、文本等）。"""
    name: str = "Read"
    description: str = """读取文件的全部内容。适用于读取任何类型的文件（代码、配置、文本等）。
如果文件很大（> 50KB），只返回前 10000 字符并提示分段读取。
使用前先确认文件路径是否正确。"""

    def _run(self, file_path: str) -> str:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            if len(content) > 50 * 1024:
                return content[:10000] + f"\n... (文件过大，只显示前 10000 字符，共 {len(content)} 字符)"
            return content
        except FileNotFoundError:
            return f"文件不存在: {file_path}"
        except UnicodeDecodeError:
            try:
                with open(file_path, "r", encoding="latin-1") as f:
                    content = f.read()
                return content
            except Exception as e:
                return f"无法解码文件 {file_path}: {e}"
        except Exception as e:
            return f"读取文件 {file_path} 失败: {e}"
