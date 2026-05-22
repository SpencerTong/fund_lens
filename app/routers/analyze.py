from fastapi import APIRouter, HTTPException
from app.models.financial import AnalyzeRequest, AnalyzeResponse
from app.services import claude_client, prompt_builder, market_data
from app.core.config import settings

router = APIRouter()

_SYSTEM = (
    "You are a senior financial analyst specializing in PE-backed businesses. "
    "Always respond with valid JSON matching the requested schema."
)


@router.post(
    "/analyze",
    response_model=AnalyzeResponse,
    tags=["Analysis"],
    summary="Analyze a company's financial health",
)
async def analyze(request: AnalyzeRequest) -> AnalyzeResponse:
    """
    Submit structured financial metrics for a single company and receive an AI-generated assessment.

    **What you get back:**
    - `analysis` — 2–3 paragraph narrative on the company's overall financial position
    - `key_insights` — the most important data-driven observations (e.g. "Rule of 40 score of 87 is top-decile for SaaS")
    - `risk_flags` — specific concerns that warrant attention (e.g. "18-month runway requires a raise within 9 months")
    - `recommendations` — concrete next steps for the CFO or PE sponsor

    **Only `company_name` and `revenue` are required.** Add more fields for a richer analysis.
    Use `focus_areas` to direct attention toward specific topics like `"liquidity"` or `"burn efficiency"`.
    """
    mkt = await market_data.get_market_context(settings.tavily_api_key)
    prompt = prompt_builder.build_analyze_prompt(request, market_context=mkt)
    try:
        result = await claude_client.analyze_financials(system=_SYSTEM, user_prompt=prompt)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Claude API error: {e}") from e

    return AnalyzeResponse(
        company_name=request.metrics.company_name,
        analysis=result.get("analysis", ""),
        key_insights=result.get("key_insights", []),
        risk_flags=result.get("risk_flags", []),
        recommendations=result.get("recommendations", []),
    )
