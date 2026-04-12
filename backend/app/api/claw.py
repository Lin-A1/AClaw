"""聊天 API 路由"""
from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel


router = APIRouter()


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    session_id: str



@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    return ChatResponse(response="", session_id="")
