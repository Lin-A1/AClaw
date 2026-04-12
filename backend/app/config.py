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
                "params": {},
            },
        },
        "paths": {
            "memory": "memory",
            "skills": "skills",
            "mcp": "mcp",
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
def server():
    return _config.server


def llm():
    return _config.server.llm
