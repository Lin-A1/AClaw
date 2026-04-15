"""
Config — 配置读写，读 settings 和 .env。
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Annotated, Literal

from dotenv import load_dotenv
from langchain_core.tools import tool
from pydantic import BaseModel, Field

_ROOT = Path(__file__).parent.parent.parent.parent
_ENV_FILE = _ROOT / ".env"
_CONFIG_FILE = _ROOT / ".claw" / "config.json"


class ConfigInput(BaseModel):
    action: Annotated[
        Literal["get", "list", "set"],
        Field(description="操作：get=读取指定 key，list=列出所有，set=写入 key"),
    ]
    key: Annotated[str | None, Field(default=None, description="配置 key（get/set 用）")] = None
    value: Annotated[str | None, Field(default=None, description="配置值（set 用）")] = None
    scope: Annotated[
        Literal["env", "config"],
        Field(default="env", description="作用域：env=.env，config=.claw/config.json"),
    ] = "env"


@tool(args_schema=ConfigInput)
def config(action: str, key: str | None = None, value: str | None = None, scope: str = "env") -> str:
    """
    读写项目配置。

    - action=get: 读取指定 key 的值（scope 决定来源）
    - action=list: 列出所有配置（scope 决定范围）
    - action=set: 写入 key=value 到 .env 或 .claw/config.json

    scope=env 读写 .env 文件（运行时配置，存储 API Key 等）
    scope=config 读写 .claw/config.json（元信息，name/version 等）
    """
    if scope == "env":
        if action == "get":
            if not key:
                return "[错误] get 需要指定 key"
            load_dotenv(_ENV_FILE, override=False)
            val = os.environ.get(key, "")
            return f"{key}={val}" if val else f"[未找到] {key}"

        if action == "list":
            if not _ENV_FILE.exists():
                return "[.env 文件不存在]"
            pairs = []
            for line in _ENV_FILE.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    pairs.append(f"  {k.strip()}={v.strip()!r}")
            return "\n".join(["# .env"] + (pairs or ["  (空)"]))

        if action == "set":
            if not key or value is None:
                return "[错误] set 需要指定 key 和 value"
            env_vars = {}
            if _ENV_FILE.exists():
                for line in _ENV_FILE.read_text(encoding="utf-8").splitlines():
                    stripped = line.strip()
                    if stripped and not stripped.startswith("#") and "=" in stripped:
                        k, v = stripped.split("=", 1)
                        env_vars[k.strip()] = v.strip()
            env_vars[key] = value
            lines = [f"{k}={v}" for k, v in env_vars.items()]
            _ENV_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")
            # reload
            load_dotenv(_ENV_FILE, override=True)
            return f"[已写入] {key}={value!r} → .env"

    elif scope == "config":
        if not _CONFIG_FILE.exists():
            return "[.claw/config.json 不存在]"

        try:
            cfg = json.loads(_CONFIG_FILE.read_text(encoding="utf-8"))
        except Exception as exc:
            return f"[错误] 读取 config.json 失败: {exc}"

        if action == "get":
            if not key:
                return "[错误] get 需要指定 key"
            val = cfg.get(key, "")
            return json.dumps({key: val}, ensure_ascii=False, indent=2)

        if action == "list":
            return json.dumps(cfg, ensure_ascii=False, indent=2)

        if action == "set":
            if not key or value is None:
                return "[错误] set 需要指定 key 和 value"
            cfg[key] = value
            _CONFIG_FILE.write_text(json.dumps(cfg, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            return f"[已写入] {key}={value!r} → .claw/config.json"
