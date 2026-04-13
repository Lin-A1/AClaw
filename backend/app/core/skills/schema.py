"""Skill 数据结构"""
from dataclasses import dataclass, field


@dataclass
class SkillInput:
    type: str = "string"
    description: str = ""
    required: bool = False


@dataclass
class SkillDefinition:
    name: str
    description: str
    prompt_template: str
    language: str = "zh"
    inputs: dict[str, SkillInput] = field(default_factory=dict)
    tags: list[str] = field(default_factory=list)
    source_file: str = ""
