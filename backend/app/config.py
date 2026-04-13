"""配置读取层 - 唯一读取 .claw/config.json 的地方"""
import json
import os
from app.schema import AppConfig

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CONFIG_DIR = os.path.join(ROOT, ".claw")
CONFIG_PATH = os.path.join(CONFIG_DIR, "config.json")


def _default_config() -> dict:
    return {
        "name": "MultClaw",
        "role": "",
        "description": "",
        "version": "0.0.1",
        "port": 18000,
        "server": {
            "llm": {
                "name": "gpt-4o",
                "url": "https://api.openai.com/v1",
                "apikey": "",
                "params": {
                    "temperature": 0.7,
                    "enable_thinking": True,
                    "reasoning_split": True,
                    "max_tokens": 8192,
                    "max_iterations": 20,
                },
            },
            "agent": {
                "language": "zh",
                "enable_cot": True,
                "enable_subagent": False,
                "memory_flush_threshold": 0.8,
                "session_max_messages": 50,
            },
        },
        "paths": {
            "memory": ".claw/memory",
            "skills": ".claw/skills",
            "mcp": ".claw/mcp",
            "prompts": ".claw/prompts",
        },
    }


def _load() -> AppConfig:
    os.makedirs(CONFIG_DIR, exist_ok=True)
    if not os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(_default_config(), f, indent=2, ensure_ascii=False)
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        cfg = AppConfig.model_validate(json.load(f))
    cfg.paths.ensure_paths(CONFIG_DIR)
    return cfg


_config = _load()


def get(key: str, default=None):
    """支持点分路径，如 get("server.llm.name")"""
    keys = key.split(".")
    val = _config.model_dump()
    for k in keys:
        if isinstance(val, dict):
            val = val.get(k)
        else:
            return default
        if val is None:
            return default
    return val


# typed 访问器
def app() -> AppConfig:
    return _config


def server():
    return _config.server


def llm():
    return _config.server.llm


def agent():
    return _config.server.agent


def paths():
    return _config.paths


def config_dir() -> str:
    return CONFIG_DIR
