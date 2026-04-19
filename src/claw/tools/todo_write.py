"""
TodoWrite — Todo 列表管理，读写 .claw/todo.json。
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Annotated, Literal

from langchain_core.tools import tool
from pydantic import BaseModel, Field

from claw.utils.logger import logger

_TODO_FILE = Path(__file__).parent.parent.parent.parent / ".claw" / "todo.json"


def _load() -> dict:
    if _TODO_FILE.exists():
        try:
            return json.loads(_TODO_FILE.read_text(encoding="utf-8"))
        except Exception:
            return {"todos": []}
    return {"todos": []}


def _save(data: dict) -> None:
    _TODO_FILE.parent.mkdir(parents=True, exist_ok=True)
    try:
        _TODO_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception as e:
        logger.error(f"todo_write 保存失败: {e}")
        raise


class TodoWriteInput(BaseModel):
    action: Annotated[
        Literal["list", "add", "done", "remove", "clear"],
        Field(description="操作：list=列出所有，add=新增，done=标记完成，remove=删除，clear=清空"),
    ]
    content: Annotated[str | None, Field(default=None, description="任务描述（add/remove 用）")] = None
    index: Annotated[int | None, Field(default=None, description="任务编号（done/remove 用，1-based）")] = None


@tool(args_schema=TodoWriteInput)
def todo_write(action: str, content: str | None = None, index: int | None = None) -> str:
    """
    管理 Todo 列表，支持 list / add / done / remove / clear。

    - action=list: 列出所有任务
    - action=add: 新增任务（content）
    - action=done: 标记完成（index，1-based）
    - action=remove: 删除任务（index，1-based）
    - action=clear: 清空所有已完成任务
    """
    data = _load()
    todos: list[dict] = data.setdefault("todos", [])

    match action:
        case "list":
            if not todos:
                return "[无任务]"
            lines = []
            for i, t in enumerate(todos, 1):
                status = "[x]" if t.get("done") else "[ ]"
                lines.append(f"  {i}. {status} {t.get('content', '')}")
            return "\n".join(["# Todo 列表"] + lines)

        case "add":
            if not content:
                return "[错误] add 需要指定 content"
            todos.append({"content": content, "done": False})
            _save(data)
            return f"[已添加] #{len(todos)} — {content}"

        case "done":
            if index is None:
                return "[错误] done 需要指定 index"
            if not (1 <= index <= len(todos)):
                return f"[错误] index 超出范围 (1-{len(todos)})"
            todos[index - 1]["done"] = True
            _save(data)
            return f"[已完成] #{index}"

        case "remove":
            if index is None:
                return "[错误] remove 需要指定 index"
            if not (1 <= index <= len(todos)):
                return f"[错误] index 超出范围 (1-{len(todos)})"
            removed = todos.pop(index - 1)
            _save(data)
            return f"[已删除] #{index} — {removed.get('content')}"

        case "clear":
            before = len(todos)
            todos[:] = [t for t in todos if not t.get("done")]
            _save(data)
            return f"[已清空] 删除了 {before - len(todos)} 项"

        case _:
            return f"[错误] 未知 action: {action}"
