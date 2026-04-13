"""Skill 注册表"""
from dataclasses import dataclass
from app.core.skills.schema import SkillDefinition
from app.core.skills.loader import SkillLoader


@dataclass
class SkillIndex:
    """Skill 索引条目 - 始终注入系统提示词，供 LLM 决策"""
    name: str
    description: str
    path: str
    tags: list[str]


class SkillRegistry:
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

    def index(self) -> list[SkillIndex]:
        """返回所有 skills 的索引信息，供系统提示词使用"""
        return [
            SkillIndex(
                name=s.name,
                description=s.description,
                path=s.source_file,
                tags=s.tags,
            )
            for s in self._skills.values()
        ]

    def build_skills_list(self) -> str:
        skills = self.list_all()
        if not skills:
            return "（暂无配置的技能）"
        lines = [f"- **{s.name}**: {s.description}" for s in skills]
        return "\n".join(lines)

    def match(self, _message: str, _history=None) -> list[SkillDefinition]:
        """保留接口签名，实际不再需要关键词匹配"""
        return []
