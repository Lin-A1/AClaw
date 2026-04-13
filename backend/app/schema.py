"""配置 schema 验证层"""
import os
from pydantic import BaseModel, Field


# ──────────────────────────────────────────
# LLM 配置
# ──────────────────────────────────────────
class LLMParams(BaseModel):
    temperature: float = 0.7
    enable_thinking: bool = True
    reasoning_split: bool = True
    max_tokens: int = 8192
    max_iterations: int = 20


class LLMConfig(BaseModel):
    name: str
    url: str
    apikey: str
    params: LLMParams = Field(default_factory=LLMParams)


# ──────────────────────────────────────────
# Agent 行为配置
# ──────────────────────────────────────────
class AgentConfig(BaseModel):
    language: str = "zh"
    enable_cot: bool = True
    enable_subagent: bool = False
    memory_flush_threshold: float = 0.8
    session_max_messages: int = 50


# ──────────────────────────────────────────
# 服务器配置
# ──────────────────────────────────────────
class ServerConfig(BaseModel):
    llm: LLMConfig
    agent: AgentConfig = Field(default_factory=AgentConfig)


# ──────────────────────────────────────────
# 路径配置
# ──────────────────────────────────────────
class PathsConfig(BaseModel):
    memory: str = ".claw/memory"
    skills: str = ".claw/skills"
    mcp: str = ".claw/mcp"
    prompts: str = ".claw/prompts"

    def ensure_paths(self, base: str = "") -> None:
        dirs = [self.memory, self.skills, self.mcp, self.prompts]
        subdirs = [
            os.path.join(self.memory, "session"),
            os.path.join(self.memory, "longterm"),
            os.path.join(self.prompts, "fragments"),
        ]
        for path in dirs + subdirs:
            full = os.path.join(base, path) if base else path
            os.makedirs(full, exist_ok=True)

    def abs(self, name: str, base: str) -> str:
        return os.path.join(base, getattr(self, name))


# ──────────────────────────────────────────
# 顶层 AppConfig
# ──────────────────────────────────────────
class AppConfig(BaseModel):
    name: str = "MultClaw"
    role: str = ""
    description: str = ""
    version: str = "0.0.1"
    port: int = Field(default=18000, ge=1, le=65535)
    server: ServerConfig
    paths: PathsConfig = Field(default_factory=PathsConfig)

