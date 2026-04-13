"""Skill 查询 API"""
from fastapi import APIRouter
from app.core.skills.registry import SkillRegistry
from app import config

router = APIRouter()


def get_skill_registry() -> SkillRegistry:
    paths = config.paths()
    cfg_dir = config.config_dir()
    registry = SkillRegistry()
    registry.load_from_dir(paths.abs("skills", cfg_dir))
    return registry


@router.get("/skills")
async def list_skills():
    registry = get_skill_registry()
    skills = registry.list_all()
    return {
        "skills": [
            {
                "name": s.name,
                "description": s.description,
                "language": s.language,
                "tags": s.tags,
            }
            for s in skills
        ]
    }


@router.get("/skills/{name}")
async def get_skill(name: str):
    registry = get_skill_registry()
    skill = registry.get(name)
    if not skill:
        return {"error": "Skill not found"}
    return {
        "name": skill.name,
        "description": skill.description,
        "language": skill.language,
        "tags": skill.tags,
        "prompt_template": skill.prompt_template,
        "inputs": skill.inputs,
    }
