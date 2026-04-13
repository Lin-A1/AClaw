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
    """系统提示词构建 - 组合记忆和技能"""

    def __init__(
        self,
        cfg: PromptBuilderConfig,
        prompt_mgr: PromptManager,
        memory: MemoryStore,
        skills_list: str = "",
    ):
        self._cfg = cfg
        self._prompt = prompt_mgr
        self._memory = memory
        self._skills_list = skills_list

    def build(self, session_id: str) -> str:
        template = self._prompt.get_system_template()
        memory_context = self._memory.build_system_context(session_id)

        return self._prompt.render(
            template,
            agent_name=self._cfg.agent_name,
            agent_role=self._cfg.agent_role,
            agent_description=self._cfg.agent_description,
            memory_context=memory_context,
            skills_list=self._skills_list,
            current_time=datetime.now().strftime("%Y-%m-%d %H:%M"),
        )
