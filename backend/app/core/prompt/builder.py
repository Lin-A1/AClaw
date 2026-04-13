"""系统提示词构建器"""
from datetime import datetime
from dataclasses import dataclass
from app.core.prompt.manager import PromptManager
from app.core.memory.store import MemoryStore


@dataclass
class PromptBuilderConfig:
    agent_name: str
    agent_role: str
    agent_description: str


class SystemPromptBuilder:
    """系统提示词构建 - 组合记忆和技能（按需注入）"""

    def __init__(
        self,
        cfg: PromptBuilderConfig,
        prompt_mgr: PromptManager,
        memory: MemoryStore,
    ):
        self._cfg = cfg
        self._prompt = prompt_mgr
        self._memory = memory

    def build(self, session_id: str, message: str = "", history: list | None = None, skills_registry=None) -> str:
        template = self._prompt.get_system_template()
        memory_context = self._memory.build_system_context(session_id)

        # 按需注入匹配的技能
        skills_context = ""
        if skills_registry is not None:
            matched = skills_registry.match(message, history)
            if matched:
                blocks = []
                from jinja2 import Template
                for s in matched:
                    blocks.append(Template(s.prompt_template).render())
                skills_context = "\n\n".join(blocks)

        return self._prompt.render(
            template,
            agent_name=self._cfg.agent_name,
            agent_role=self._cfg.agent_role,
            agent_description=self._cfg.agent_description,
            memory_context=memory_context,
            skills_context=skills_context,
            current_time=datetime.now().strftime("%Y-%m-%d %H:%M"),
        )
