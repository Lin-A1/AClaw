"""配置 schema 验证层"""
import os
from pydantic import BaseModel, Field


class LLMConfig(BaseModel):
    name: str
    url: str
    apikey: str
    params: dict = Field(default_factory=dict)


class PathsConfig(BaseModel):
    memory: str
    skills: str
    mcp: str

    def ensure_paths(self, base: str = "") -> None:
        for path in [self.memory, self.skills, self.mcp]:
            full = os.path.join(base, path) if path else base
            os.makedirs(full, exist_ok=True)


class AppConfig(BaseModel):
    name: str = "MultClaw"
    role: str = ""
    description: str = ""
    version: str = "0.0.1"
    port: int = Field(default=18000, ge=1, le=65535)
    paths: PathsConfig

