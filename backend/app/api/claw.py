"""聊天 API 路由"""
import uuid
from typing import Optional, AsyncIterator

from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import json

from app.core.agent.claw_agent import ClawAgent

router = APIRouter()
_agent: Optional[ClawAgent] = None


async def get_agent() -> ClawAgent:
    global _agent
    if _agent is None:
        _agent = await ClawAgent.from_config()
    return _agent


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    stream: bool = False


class ChatResponse(BaseModel):
    response: str
    session_id: str
    finish_reason: str = "stop"


@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    agent = await get_agent()
    output = await agent.run(req.message, req.session_id)
    return ChatResponse(
        response=output.response,
        session_id=output.session_id,
        finish_reason=output.finish_reason,
    )


@router.post("/chat/stream")
async def chat_stream(req: ChatRequest):
    """SSE 流式聊天"""
    agent = await get_agent()
    session_id = req.session_id or str(uuid.uuid4())

    async def event_generator() -> AsyncIterator[str]:
        async for chunk in agent.stream(req.message, session_id):
            data = json.dumps(
                {
                    "type": chunk.type,
                    "content": chunk.content,
                    "tool_name": chunk.tool_name,
                    "session_id": chunk.session_id,
                },
                ensure_ascii=False,
            )
            yield f"data: {data}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"X-Session-Id": session_id},
    )
