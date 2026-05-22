from fastapi import APIRouter, HTTPException
from app.models.financial import CompareRequest, CompareResponse
from app.services import claude_client, prompt_builder, market_data
from app.core.config import settings

router = APIRouter()

_SYSTEM = (
    "You are a senior financial analyst advising a PE fund. "
    "Always respond with valid JSON matching the requested schema."
)


@router.post(
    "/portfolio/compare",
    response_model=CompareResponse,
    tags=["Portfolio"],
    summary="Compare two portfolio companies side-by-side",
)
async def compare(request: CompareRequest) -> CompareResponse:
    """
    Submit financial metrics for two companies and receive a structured side-by-side comparison.

    **What you get back:**
    - `comparison` — multi-paragraph narrative comparing the two companies across key dimensions
    - `winner_by_category` — a verdict for each of: `growth`, `profitability`, `efficiency`, `financial_health`
      (value is the winning company's name, or `"Tie"`)
    - `summary` — one or two sentence overall verdict

    Use `comparison_criteria` to focus the analysis on specific dimensions, e.g.
    `["burn efficiency", "gross margin quality", "growth sustainability"]`.
    """
    mkt = await market_data.get_market_context(settings.tavily_api_key)
    prompt = prompt_builder.build_compare_prompt(request, market_context=mkt)
    try:
        result = await claude_client.compare_companies(system=_SYSTEM, user_prompt=prompt)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Claude API error: {e}") from e

    return CompareResponse(
        company_a_name=request.company_a.company_name,
        company_b_name=request.company_b.company_name,
        comparison=result.get("comparison", ""),
        winner_by_category=result.get("winner_by_category", {}),
        summary=result.get("summary", ""),
    )
