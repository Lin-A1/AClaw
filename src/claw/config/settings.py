"""
统一配置入口。

加载优先级：
1. .env（密钥、运行时参数）  — 通过 python-dotenv 加载
2. .claw/config.json（元信息） — 项目共享的结构化配置

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
    system_prompt: str = "You are a helpful AI assistant."

    @property
    def api_base(self) -> str:
        return f"{self.url.rstrip('/')}/messages"


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
    project: Project = Field(default_factory=Project)


# ---------------------------------------------------------------------------
# 全局单例（懒加载，线程安全）
# ---------------------------------------------------------------------------

@lru_cache(maxsize=1)
def get_settings() -> Settings:
    load_dotenv(_ROOT / ".env", override=False)

    project_meta: dict[str, Any] = {}
    config_path = _ROOT / ".claw" / "config.json"
    if config_path.exists():
        with open(config_path, encoding="utf-8") as f:
            project_meta = json.load(f)

    def env(key: str, fallback: str = "") -> str:
        return os.environ.get(key, fallback)

    return Settings(
        llm=LLM(
            name=env("MODEL_NAME", "MiniMax-M2.7"),
            url=env("MODEL_URL", "https://api.minimaxi.com/v1"),
            api_key=env("MODEL_APIKEY", ""),
            max_tokens=int(env("MAX_TOKENS", "4096")),
            temperature=float(env("TEMPERATURE", "1.0")),
            system_prompt=env("SYSTEM_PROMPT", "You are a helpful AI assistant."),
        ),
        server=Server(
            host=env("API_HOST", "0.0.0.0"),
            port=int(env("API_PORT", "18000")),
        ),
        log=Log(
            level=env("LOG_LEVEL", "INFO"),
        ),
        project=Project(**project_meta),
    )


# 全局单例，供外部直接导入
settings = get_settings()
