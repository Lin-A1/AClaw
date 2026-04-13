"""Skill 注册表"""
from app.core.skills.schema import SkillDefinition
from app.core.skills.loader import SkillLoader


class SkillRegistry:
    """Skill 注册和管理"""

    def __init__(self):
        self._skills: dict[str, SkillDefinition] = {}

    def load_from_dir(self, skills_dir: str) -> None:
        loader = SkillLoader()
        for skill in loader.load_from_dir(skills_dir):
            self._skills[skill.name] = skill

    def register(self, skill: SkillDefinition) -> None:
        self._skills[skill.name] = skill

    def get(self, name: str) -> SkillDefinition | None:
        return self._skills.get(name)

    def list_all(self) -> list[SkillDefinition]:
        return list(self._skills.values())

    def as_langchain_tools(self) -> list:
        from app.core.skills.tool_adapter import SkillToolAdapter
        return [SkillToolAdapter(s) for s in self._skills.values()]

    def build_skills_list(self) -> str:
        skills = self.list_all()
        if not skills:
            return "（暂无配置的技能）"
        lines = [f"- **{s.name}**: {s.description}" for s in skills]
        return "\n".join(lines)
