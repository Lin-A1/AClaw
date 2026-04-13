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

    def build_skills_list(self) -> str:
        skills = self.list_all()
        if not skills:
            return "（暂无配置的技能）"
        lines = [f"- **{s.name}**: {s.description}" for s in skills]
        return "\n".join(lines)

    def match(self, message: str, history: list[dict] | None = None) -> list[SkillDefinition]:
        """根据消息内容匹配相关技能（基于关键词相关性）"""
        if not self._skills:
            return []
        message_lower = message.lower()
        scored = []
        for skill in self._skills.values():
            score = 0
            # 名字匹配（最高权重）
            if any(kw in skill.name.lower() for kw in message_lower.split()):
                score += 3
            # 描述匹配
            desc_lower = skill.description.lower()
            for kw in message_lower.split():
                if kw in desc_lower:
                    score += 2
            # 标签匹配
            for tag in skill.tags:
                if tag.lower() in message_lower:
                    score += 2
            # 模板关键词匹配
            for kw in message_lower.split():
                if len(kw) > 2 and kw in skill.prompt_template.lower():
                    score += 1
            if score > 0:
                scored.append((score, skill))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [s for _, s in scored]
