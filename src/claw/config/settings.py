"""
统一配置入口。

加载优先级（从高到低）：
1. 环境变量（运行时动态覆盖，如 MODEL_APIKEY）
2. .claw/config.json（项目共享的非敏感配置）
3. 代码默认值（绝对兜底）

使用方式：
    from claw.config.settings import settings

    # 传给 langchain_openai.ChatOpenAI（MiniMax 等 OpenAI 兼容 API）
    ChatOpenAI(
        model=settings.llm.name,
        api_key=settings.llm.api_key,
        base_url=settings.llm.url,
        max_tokens=settings.llm.max_tokens,
    )
"""

from __future__ import annotations

import json
import os
from functools import lru_cache
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# 路径解析
# ---------------------------------------------------------------------------
# src/claw/config/settings.py  →  项目根目录
_ROOT = Path(__file__).parent.parent.parent.parent


# ---------------------------------------------------------------------------
# 子配置模型
# ---------------------------------------------------------------------------

class LLM(BaseModel):
    name: str = "MiniMax-M2.7"
    url: str = "https://api.minimaxi.com/v1"
    api_key: str = ""
    max_tokens: int = 4096
    temperature: float = 1.0

    @property
    def api_base(self) -> str:
        return f"{self.url.rstrip('/')}/messages"


class Memory(BaseModel):
    root: Path = Field(default_factory=lambda: _ROOT / ".claw" / "memory")
    db_path: Path = Field(default_factory=lambda: _ROOT / ".claw" / "memory" / "session.db")


class Server(BaseModel):
    host: str = "0.0.0.0"
    port: int = 18000


class Log(BaseModel):
    level: str = "INFO"


class Project(BaseModel):
    name: str = "AClaw"
    role: str = "claw-agent"
    description: str = "Agent Framework"
    version: str = "0.1.0"
    port: int = 18000


# ---------------------------------------------------------------------------
# 聚合配置
# ---------------------------------------------------------------------------

class Settings(BaseModel):
    llm: LLM = Field(default_factory=LLM)
    server: Server = Field(default_factory=Server)
    log: Log = Field(default_factory=Log)
    memory: Memory = Field(default_factory=Memory)
    project: Project = Field(default_factory=Project)


# ---------------------------------------------------------------------------
# 全局单例（懒加载，线程安全）
# ---------------------------------------------------------------------------

@lru_cache(maxsize=1)
def get_settings() -> Settings:
    load_dotenv(_ROOT / ".env", override=False)

    config_meta: dict[str, Any] = {}
    config_path = _ROOT / ".claw" / "config.json"
    if config_path.exists():
        with open(config_path, encoding="utf-8") as f:
            config_meta = json.load(f)

    def env(key: str, fallback: str = "") -> str:
        return os.environ.get(key, fallback)

    llm_meta: dict[str, Any] = config_meta.get("llm", {})
    server_meta: dict[str, Any] = config_meta.get("server", {})
    log_meta: dict[str, Any] = config_meta.get("log", {})
    memory_meta: dict[str, Any] = config_meta.get("memory", {})

    memory_root_env = env("CLAW_MEMORY_DIR", "")
    memory_root = (
        Path(memory_root_env)
        if memory_root_env
        else Path(memory_meta.get("root", str(_ROOT / ".claw" / "memory")))
    )

    return Settings(
        llm=LLM(
            name=env("MODEL_NAME", llm_meta.get("name", "MiniMax-M2.7")),
            url=env("MODEL_URL", llm_meta.get("url", "https://api.minimaxi.com/v1")),
            api_key=env("MODEL_APIKEY", ""),
            max_tokens=int(env("MAX_TOKENS", str(llm_meta.get("max_tokens", 4096)))),
            temperature=float(env("TEMPERATURE", str(llm_meta.get("temperature", 1.0)))),
        ),
        server=Server(
            host=env("API_HOST", server_meta.get("host", "0.0.0.0")),
            port=int(env("API_PORT", str(server_meta.get("port", 18000)))),
        ),
        log=Log(
            level=env("LOG_LEVEL", log_meta.get("level", "INFO")),
        ),
        memory=Memory(
            root=memory_root,
            db_path=memory_root / "session.db",
        ),
        project=Project(**config_meta),
    )


# 全局单例，供外部直接导入
settings = get_settings()
