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
    property_id: str | None = None
    active_filters: dict[str, Any] = Field(default_factory=dict)
    selected_property: dict[str, Any] = Field(default_factory=dict)
    model: str | None = None


class ChatResponse(BaseModel):
    message: str
    provider: str
    thread_id: str | None = None


@router.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest) -> ChatResponse:
    raw_messages: list[dict[str, Any]] = [m.model_dump() for m in req.messages]
    if req.property_id or req.active_filters or req.selected_property:
        context = {
            "property_id": req.property_id,
            "active_filters": req.active_filters,
            "selected_property": req.selected_property,
        }
        raw_messages = [
            {
                "role": "system",
                "content": (
                    "Use this Bulgaria real-estate UI context when it is relevant. "
                    "Do not invent missing property facts. "
                    f"context={context}"
                ),
            },
            *raw_messages,
        ]
    text, provider = run_chat_completion(raw_messages, model=req.model)
    return ChatResponse(message=text, provider=provider, thread_id=req.thread_id)
