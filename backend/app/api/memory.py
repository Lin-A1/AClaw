"""记忆管理 API"""
from fastapi import APIRouter
from pydantic import BaseModel
from app.core.agent.claw_agent import ClawAgent
from app.core.memory.store import MemoryStore, MemoryConfig
from app import config

router = APIRouter()


class MemoryContent(BaseModel):
    content: str


async def get_memory_store() -> MemoryStore:
    paths = config.paths()
    cfg_dir = config.config_dir()
    agent_cfg = config.agent()
    return MemoryStore(MemoryConfig(
        base_dir=paths.abs("memory", cfg_dir),
        session_max_messages=agent_cfg.session_max_messages,
        flush_threshold=agent_cfg.memory_flush_threshold,
    ))


@router.get("/memory/user")
async def get_user_memory():
    memory = await get_memory_store()
    return {"content": memory.user.load()}


@router.put("/memory/user")
async def update_user_memory(body: MemoryContent):
    memory = await get_memory_store()
    memory.user.save(body.content)
    return {"ok": True}


@router.get("/memory/preferences")
async def get_preferences():
    memory = await get_memory_store()
    return {"content": memory.preferences.load()}


@router.put("/memory/preferences")
async def update_preferences(body: MemoryContent):
    memory = await get_memory_store()
    memory.preferences.save(body.content)
    return {"ok": True}


@router.get("/memory/sessions")
async def list_sessions():
    memory = await get_memory_store()
    return {"sessions": memory.session.list_sessions()}


@router.delete("/memory/sessions/{session_id}")
async def delete_session(session_id: str):
    memory = await get_memory_store()
    memory.session.clear(session_id)
    return {"ok": True}


@router.get("/memory/sessions/{session_id}/history")
async def get_session_history(session_id: str):
    memory = await get_memory_store()
    return {"messages": memory.session.get_messages(session_id)}
