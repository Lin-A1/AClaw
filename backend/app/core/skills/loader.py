"""Skill 加载器 - 从 .claw/skills/*.md 加载"""
import os
from app.core.skills.schema import SkillDefinition, SkillInput


class SkillLoader:
    """从 Markdown 文件加载 Skill 定义"""

    def load_from_dir(self, skills_dir: str) -> list[SkillDefinition]:
        if not os.path.exists(skills_dir):
            return []
        skills = []
        for fname in os.listdir(skills_dir):
            if not fname.endswith(".md"):
                continue
            path = os.path.join(skills_dir, fname)
            skills.append(self._load_file(path))
        return skills

    def _load_file(self, path: str) -> SkillDefinition:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        return self._parse(content, path)

    def _parse(self, content: str, source_file: str) -> SkillDefinition:
        lines = content.split("\n")
        metadata = {}
        body_lines = []
        in_frontmatter = False

        for line in lines:
            if line.strip() == "---":
                in_frontmatter = not in_frontmatter
                continue
            if in_frontmatter:
                if ":" in line:
                    key, value = line.split(":", 1)
                    metadata[key.strip()] = value.strip()
            else:
                body_lines.append(line)

        inputs = {}
        if "input" in metadata:
            inputs = {}

        return SkillDefinition(
            name=metadata.get("name", os.path.splitext(os.path.basename(source_file))[0]),
            description=metadata.get("description", ""),
            prompt_template="\n".join(body_lines).strip(),
            language=metadata.get("language", "zh"),
            tags=self._parse_tags(metadata.get("tags", "")),
            source_file=source_file,
        )

    def _parse_tags(self, tags_str: str) -> list[str]:
        if not tags_str:
            return []
        tags_str = tags_str.strip("[]")
        return [t.strip() for t in tags_str.split(",") if t.strip()]
