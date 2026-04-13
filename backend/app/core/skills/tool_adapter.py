"""Skill → LangChain Tool 适配器"""
from jinja2 import Template
from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool
from app.core.skills.schema import SkillDefinition


class SkillToolAdapter(BaseTool):
    """将 SkillDefinition 包装为 LangChain Tool"""

    skill_def: SkillDefinition = Field(default=None, exclude=True)

    @property
    def skill(self) -> SkillDefinition:
        return self.skill_def

    def __init__(self, skill: SkillDefinition, **kwargs):
        name = f"skill_{skill.name}"
        description = f"[Skill] {skill.description}"
        super().__init__(name=name, description=description)
        self.skill_def = skill

    def _run(self, **kwargs) -> str:
        if not self.skill_def:
            return "Skill not initialized"
        tpl = Template(self.skill_def.prompt_template)
        return tpl.render(**kwargs)

    async def _arun(self, **kwargs) -> str:
        return self._run(**kwargs)
