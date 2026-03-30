"""配置读取层 - 唯一读取 .claw/config.json 的地方"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CONFIG_PATH = os.path.join(ROOT, ".claw", "config.json")


def _load() -> dict:
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


_config = _load()


def get(key: str, default=None):
    """支持点分路径，如 get("server.llm.name")"""
    keys = key.split(".")
    val = _config
    for k in keys:
        if isinstance(val, dict):
            val = val.get(k)
        else:
            return default
        if val is None:
            return default
    return val
