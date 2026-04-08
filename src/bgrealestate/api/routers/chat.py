from __future__ import annotations

from typing import Any, Literal

from fastapi import APIRouter
from pydantic import BaseModel, Field

from ...services.chat_service import run_chat_completion

router = APIRouter(tags=["chat"])


class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    messages: list[ChatMessage] = Field(min_length=1)
    thread_id: str | None = None
    model: str | None = None


class ChatResponse(BaseModel):
    message: str
    provider: str
    thread_id: str | None = None


@router.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest) -> ChatResponse:
    raw_messages: list[dict[str, Any]] = [m.model_dump() for m in req.messages]
    text, provider = run_chat_completion(raw_messages, model=req.model)
    return ChatResponse(message=text, provider=provider, thread_id=req.thread_id)
