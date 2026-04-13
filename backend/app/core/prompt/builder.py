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
    """系统提示词构建 - 记忆 + 全量 skills 索引始终注入"""

    def __init__(
        self,
        cfg: PromptBuilderConfig,
        prompt_mgr: PromptManager,
        memory: MemoryStore,
    ):
        self._cfg = cfg
        self._prompt = prompt_mgr
        self._memory = memory

    def build(
        self,
        session_id: str,
        skills_registry=None,
        activated_skill_name: str | None = None,
    ) -> str:
        template = self._prompt.get_system_template()
        memory_context = self._memory.build_system_context(session_id)

        # 始终注入全量 skills 索引（供 LLM 决策激活哪个）
        skills_index_lines: list[str] = []
        if skills_registry is not None:
            for idx in skills_registry.index():
                tags_str = f" [{', '.join(idx.tags)}]" if idx.tags else ""
                skills_index_lines.append(
                    f"- **{idx.name}**{tags_str}: {idx.description}  → {idx.path}"
                )

        # 按需注入被激活的 skill 完整内容
        activated_body = ""
        if skills_registry is not None and activated_skill_name:
            skill = skills_registry.get(activated_skill_name)
            if skill:
                activated_body = f"\n\n=== 激活技能: {skill.name} ===\n{skill.prompt_template}\n===\n"

        return self._prompt.render(
            template,
            agent_name=self._cfg.agent_name,
            agent_role=self._cfg.agent_role,
            agent_description=self._cfg.agent_description,
            memory_context=memory_context,
            skills_index=skills_index_lines,
            activated_skill_body=activated_body,
            current_time=datetime.now().strftime("%Y-%m-%d %H:%M"),
        )
