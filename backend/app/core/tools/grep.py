"""Grep tool: search for pattern in files"""
import os
import re
from pydantic import Field
from langchain_core.tools import BaseTool


class GrepTool(BaseTool):
    """在文件中搜索匹配正则表达式或字符串的内容。"""
    name: str = "Grep"
    description: str = """在文件中搜索匹配正则表达式或字符串的内容。
path 参数指定搜索目录（默认当前目录）。
pattern 参数支持正则表达式或字符串。
file_type 参数可选，如 "py"、"ts"、"md" 限制只搜索特定类型文件。
返回格式：文件路径:行号:匹配内容，每条结果一行。
max_results 限制最大返回条数（默认 100）。"""

    def _run(
        self,
        path: str = ".",
        pattern: str = "",
        file_type: str = "",
        max_results: int = 100,
    ) -> str:
        if not pattern:
            return "请提供搜索 pattern"
        try:
            re.compile(pattern)
        except re.error as e:
            return f"无效的正则表达式: {e}"

        try:
            results = []
            path = os.path.abspath(path)
            for root, _, files in os.walk(path):
                # 跳过 .git、node_modules 等目录
                skip = {'.git', 'node_modules', '__pycache__', '.venv', 'venv', '.claude'}
                if any(s in root for s in skip):
                    continue
                for fname in files:
                    if file_type and not fname.endswith(f".{file_type}"):
                        continue
                    fpath = os.path.join(root, fname)
                    try:
                        with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                            for lineno, line in enumerate(f, 1):
                                if re.search(pattern, line):
                                    rel = os.path.relpath(fpath, path)
                                    results.append(f"{rel}:{lineno}: {line.rstrip()}")
                                    if len(results) >= max_results:
                                        break
                    except Exception:
                        continue
                    if len(results) >= max_results:
                        break
                if len(results) >= max_results:
                    break

            if not results:
                return f"未在 '{path}' 中找到匹配 '{pattern}' 的内容"
            out = "\n".join(results)
            if len(results) == max_results:
                out += f"\n... (已达最大结果数 {max_results})"
            return out
        except Exception as e:
            return f"Grep 搜索失败: {e}"
