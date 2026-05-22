from __future__ import annotations
import json
import anthropic
from app.core.config import settings
from app.models.conversation import Message

_client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)


async def complete(system: str, messages: list[dict]) -> str:
    response = await _client.messages.create(
        model=settings.claude_model,
        max_tokens=settings.max_tokens,
        system=system,
        messages=messages,
    )
    return response.content[0].text


async def analyze_financials(system: str, user_prompt: str) -> dict:
    text = await complete(system=system, messages=[{"role": "user", "content": user_prompt}])
    try:
        # Strip markdown code fences if present
        cleaned = text.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("```", 2)[1]
            if cleaned.startswith("json"):
                cleaned = cleaned[4:]
            cleaned = cleaned.rsplit("```", 1)[0].strip()
        return json.loads(cleaned)
    except (json.JSONDecodeError, IndexError):
        # Fallback: return raw text wrapped in expected shape
        return {
            "analysis": text,
            "key_insights": [],
            "risk_flags": [],
            "recommendations": [],
        }


async def compare_companies(system: str, user_prompt: str) -> dict:
    text = await complete(system=system, messages=[{"role": "user", "content": user_prompt}])
    try:
        cleaned = text.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("```", 2)[1]
            if cleaned.startswith("json"):
                cleaned = cleaned[4:]
            cleaned = cleaned.rsplit("```", 1)[0].strip()
        return json.loads(cleaned)
    except (json.JSONDecodeError, IndexError):
        return {
            "comparison": text,
            "winner_by_category": {},
            "summary": "",
        }


async def chat(
    system: str,
    history: list[Message],
    new_question: str,
) -> tuple[str, list[Message]]:
    messages = [{"role": m.role, "content": m.content} for m in history]
    messages.append({"role": "user", "content": new_question})

    answer = await complete(system=system, messages=messages)

    updated_history = list(history) + [
        Message(role="user", content=new_question),
        Message(role="assistant", content=answer),
    ]
    return answer, updated_history
