"""Skill 加载器 - 支持 SKILL.md 格式（YAML frontmatter + markdown body）"""
import os
import yaml
from app.core.skills.schema import SkillDefinition


class SkillLoader:
    """支持两种格式：
    1. 目录型：skills/<name>/SKILL.md
    2. 文件型：skills/<name>.md
    """

    def load_from_dir(self, skills_dir: str) -> list[SkillDefinition]:
        if not os.path.exists(skills_dir):
            return []
        skills = []
        for entry in os.listdir(skills_dir):
            path = os.path.join(skills_dir, entry)
            if os.path.isdir(path):
                skill_md = os.path.join(path, "SKILL.md")
                if os.path.isfile(skill_md):
                    skills.append(self._load_file(skill_md))
            elif entry.endswith(".md") and os.path.isfile(path):
                skills.append(self._load_file(path))
        return skills

    def _load_file(self, path: str) -> SkillDefinition:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        return self._parse(content, path)

    def _parse(self, content: str, source_file: str) -> SkillDefinition:
        # 分离 frontmatter 和 body
        lines = content.splitlines()
        if not lines or lines[0].strip() != "---":
            return self._from_dict({}, "\n".join(lines), source_file)

        # 找到 frontmatter 结束
        fm_end = None
        for i, line in enumerate(lines[1:], 1):
            if line.strip() == "---":
                fm_end = i
                break

        if fm_end is None:
            return self._from_dict({}, "\n".join(lines[1:]), source_file)

        fm_raw = "\n".join(lines[1:fm_end])
        body = "\n".join(lines[fm_end + 1:])

        # 用 YAML 解析 frontmatter（正确处理 | 块标量）
        meta = yaml.safe_load(fm_raw) or {}
        return self._from_dict(meta, body, source_file)

    def _from_dict(self, meta: dict, body: str, source_file: str) -> SkillDefinition:
        # 从路径推断 name（目录型用目录名，文件型用文件名）
        basename = os.path.splitext(os.path.basename(source_file))[0]
        dir_name = os.path.basename(os.path.dirname(source_file))
        name = meta.get("name", dir_name if basename == "SKILL" else basename)

        desc = meta.get("description", "")
        if isinstance(desc, list):
            desc = " ".join(desc)

        return SkillDefinition(
            name=str(name),
            description=str(desc).strip(),
            prompt_template=body.strip(),
            language=str(meta.get("language", "zh")),
            tags=list(meta.get("tags", [])),
            source_file=source_file,
        )
