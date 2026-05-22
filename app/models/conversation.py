from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Literal, Optional


class Message(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class AskRequest(BaseModel):
    question: str = Field(..., min_length=1, description="CFO question or prompt")
    conversation_history: list[Message] = Field(
        default_factory=list,
        description=(
            "Prior turns for multi-turn conversation. "
            "Pass the `updated_history` from the previous response to continue the thread."
        ),
    )
    context: Optional[dict] = Field(
        None,
        description=(
            "Optional key-value facts about the company injected into Claude's system prompt. "
            'E.g. {"ARR": "$5M", "stage": "Series B", "runway": "18 months"}'
        ),
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "question": "We have 18 months of runway growing at 90% YoY. Should we raise now or wait?",
                "context": {
                    "company": "Acme SaaS",
                    "ARR": "$5M",
                    "stage": "Series B",
                    "industry": "SaaS",
                },
                "conversation_history": [],
            }
        }
    }


class AskResponse(BaseModel):
    answer: str
    updated_history: list[Message]
