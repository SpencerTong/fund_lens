from fastapi import APIRouter, HTTPException
from app.models.conversation import AskRequest, AskResponse
from app.services import claude_client, prompt_builder, market_data
from app.core.config import settings

router = APIRouter()


@router.post(
    "/ask",
    response_model=AskResponse,
    tags=["Ask"],
    summary="Ask a freeform CFO question",
)
async def ask(request: AskRequest) -> AskResponse:
    """
    Ask any finance or strategy question in plain English and get a CFO-advisor-quality answer.

    **Single turn (simplest use):** just send `question`.

    **Multi-turn conversation:** pass the `updated_history` array from the previous response
    back as `conversation_history`. Claude will remember everything said so far and answer
    in context — just like a back-and-forth with a human advisor.

    **Optional `context` field:** supply key facts about the company (e.g. ARR, stage, industry)
    as a key-value dict. These are injected into Claude's system prompt so answers are
    grounded in your actual situation rather than generic advice.

    Example `context`:
    ```json
    {"company": "Acme SaaS", "ARR": "$5M", "stage": "Series B", "runway": "18 months"}
    ```
    """
    mkt = await market_data.get_market_context(settings.tavily_api_key)
    system = prompt_builder.build_cfo_system_prompt(request.context, market_context=mkt)
    try:
        answer, updated_history = await claude_client.chat(
            system=system,
            history=request.conversation_history,
            new_question=request.question,
        )
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Claude API error: {e}") from e

    return AskResponse(answer=answer, updated_history=updated_history)
