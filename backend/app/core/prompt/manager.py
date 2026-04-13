"""提示词模板管理器"""
import os
from dataclasses import dataclass


@dataclass
class PromptManagerConfig:
    prompts_dir: str
    language: str = "zh"


class PromptManager:
    """提示词模板加载和语言切换"""

    def __init__(self, cfg: PromptManagerConfig):
        self._dir = cfg.prompts_dir
        self._language = cfg.language
        self._cache = {}

    def switch_language(self, lang: str) -> None:
        self._language = lang
        self._cache.clear()

    def get_system_template(self) -> str:
        return self._load_template(f"system.{self._language}")

    def get_fragment(self, name: str) -> str:
        return self._load_template(f"fragments/{name}")

    def render(self, template_str: str, **kwargs) -> str:
        from jinja2 import Template
        return Template(template_str).render(**kwargs)

    def _load_template(self, name: str) -> str:
        if name in self._cache:
            return self._cache[name]
        path = os.path.join(self._dir, f"{name}.md")
        if not os.path.exists(path):
            return ""
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        self._cache[name] = content
        return content
