"""Skill → LangChain Tool 适配器"""
from jinja2 import Template
from langchain_core.tools import BaseTool
from app.core.skills.schema import SkillDefinition


class SkillToolAdapter(BaseTool):
    """将 SkillDefinition 包装为 LangChain Tool"""

    skill: SkillDefinition

    @property
    def name(self) -> str:
        return f"skill_{self.skill.name}"

    @property
    def description(self) -> str:
        return f"[Skill] {self.skill.description}"

    def _run(self, **kwargs) -> str:
        tpl = Template(self.skill.prompt_template)
        return tpl.render(**kwargs)

    async def _arun(self, **kwargs) -> str:
        return self._run(**kwargs)
