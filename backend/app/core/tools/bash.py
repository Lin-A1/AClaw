"""Bash tool: execute shell commands"""
import os
import subprocess
from pydantic import Field
from langchain_core.tools import BaseTool


class BashTool(BaseTool):
    """在本地 shell 中执行命令。适用于运行脚本、安装依赖、执行 git 命令等。"""
    name: str = "Bash"
    description: str = """在本地 shell 中执行命令。适用于运行脚本、安装依赖、执行 git 命令等。
timeout 参数控制超时时间（秒），默认 60 秒。
输出受限流式返回（最多显示最后 5000 字符）。
注意：破坏性操作（rm -rf、git push --force 等）会被拒绝。"""

    def _run(self, command: str, timeout: int = 60) -> str:
        # 安全检查：禁止危险命令
        dangerous = [
            "rm -rf /", "rm -rf ~", "dd if=",
            ":(){:|:&};:",  # fork bomb
        ]
        cmd_lower = command.lower().strip()
        for d in dangerous:
            if cmd_lower.startswith(d):
                return f"拒绝执行危险命令: {command[:50]}"

        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=min(timeout, 300),
                cwd=os.getcwd(),
            )
            out = result.stdout
            err = result.stderr
            if len(out) > 5000:
                out = out[-5000:] + f"\n... (输出截断，共 {len(out)} 字符)"
            if result.returncode != 0:
                return f"[exit {result.returncode}]\n{out}\n{err}".strip()
            return out if out else "(命令执行成功，无输出)"
        except subprocess.TimeoutExpired:
            return f"命令超时（{timeout}s）: {command[:80]}"
        except Exception as e:
            return f"命令执行失败: {e}"
