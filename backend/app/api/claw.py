"""聊天 API 路由"""
from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel

from app.services.llm import get_llm_provider

router = APIRouter()


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    session_id: str


# 简单会话存储（后续可替换为数据库）
_sessions: dict[str, list[dict[str, str]]] = {}


@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    """处理用户消息，返回 AI 响应"""
    session_id = req.session_id or "default"

    # 获取或初始化会话历史
    if session_id not in _sessions:
        _sessions[session_id] = []
    messages = _sessions[session_id]

    # 添加用户消息
    messages.append({"role": "user", "content": req.message})

    # 调用 LLM
    provider = get_llm_provider()
    response_text = await provider.chat(messages)

    # 添加 AI 响应
    messages.append({"role": "assistant", "content": response_text})

    return ChatResponse(response=response_text, session_id=session_id)
