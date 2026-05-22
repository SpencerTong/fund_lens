from __future__ import annotations
from app.models.financial import FinancialMetrics, AnalyzeRequest, CompareRequest


def _format_metrics(metrics: FinancialMetrics) -> str:
    lines = [
        f"Company: {metrics.company_name}",
        f"Annual Revenue: ${metrics.revenue:,.0f}",
    ]
    if metrics.burn_rate is not None:
        lines.append(f"Monthly Burn Rate: ${metrics.burn_rate:,.0f}")
    if metrics.runway_months is not None:
        lines.append(f"Runway: {metrics.runway_months:.1f} months")
    if metrics.ebitda_margin is not None:
        lines.append(f"EBITDA Margin: {metrics.ebitda_margin:.1f}%")
    if metrics.gross_margin is not None:
        lines.append(f"Gross Margin: {metrics.gross_margin:.1f}%")
    if metrics.revenue_growth_yoy is not None:
        lines.append(f"Revenue Growth (YoY): {metrics.revenue_growth_yoy:.1f}%")
    if metrics.headcount is not None:
        lines.append(f"Headcount: {metrics.headcount}")
    if metrics.industry:
        lines.append(f"Industry: {metrics.industry}")
    if metrics.stage:
        lines.append(f"Stage: {metrics.stage}")
    return "\n".join(lines)


def build_analyze_prompt(request: AnalyzeRequest, market_context: str = "") -> str:
    metrics_text = _format_metrics(request.metrics)
    focus = ""
    if request.focus_areas:
        focus = f"\n\nPlease pay particular attention to: {', '.join(request.focus_areas)}."

    market_section = f"\n\n{market_context}" if market_context else ""

    return f"""You are a senior financial analyst specializing in PE-backed businesses. Analyze the following financial metrics and provide a comprehensive assessment.

## Financial Metrics
{metrics_text}{focus}{market_section}

## Instructions
Provide your analysis in the following JSON format:
{{
  "analysis": "<2-3 paragraph narrative analysis of the company's financial health>",
  "key_insights": ["<insight 1>", "<insight 2>", "<insight 3>"],
  "risk_flags": ["<risk 1>", "<risk 2>"],
  "recommendations": ["<recommendation 1>", "<recommendation 2>", "<recommendation 3>"]
}}

Be specific, data-driven, and actionable. Where relevant, reference the live market context above (interest rates, SaaS multiples, market sentiment). Focus on what matters most for a PE sponsor or CFO."""


def build_compare_prompt(request: CompareRequest, market_context: str = "") -> str:
    metrics_a = _format_metrics(request.company_a)
    metrics_b = _format_metrics(request.company_b)
    criteria = ""
    if request.comparison_criteria:
        criteria = f"\n\nFocus your comparison on: {', '.join(request.comparison_criteria)}."

    market_section = f"\n\n{market_context}" if market_context else ""

    return f"""You are a senior financial analyst advising a PE fund. Compare the two portfolio companies below and provide a detailed side-by-side assessment.

## Company A
{metrics_a}

## Company B
{metrics_b}{criteria}{market_section}

## Instructions
Provide your comparison in the following JSON format:
{{
  "comparison": "<3-4 paragraph narrative comparing the two companies across key dimensions>",
  "winner_by_category": {{
    "growth": "<company name or 'Tie'>",
    "profitability": "<company name or 'Tie'>",
    "efficiency": "<company name or 'Tie'>",
    "financial_health": "<company name or 'Tie'>"
  }},
  "summary": "<1-2 sentence overall verdict on which company is better positioned>"
}}

Be objective, specific, and cite the metrics to support your conclusions. Where relevant, reference the live market context above (e.g. current interest rates or public SaaS multiples as a valuation anchor)."""


def build_cfo_system_prompt(
    context: dict | None = None,  # noqa: PYI016
    market_context: str = "",
) -> str:
    base = (
        "You are an expert CFO advisor and financial analyst with deep experience in "
        "PE-backed businesses, SaaS metrics, and corporate finance. "
        "Provide concise, actionable answers grounded in financial best practices. "
        "When referencing calculations or benchmarks, be specific and cite industry standards."
    )
    if market_context:
        base += f"\n\n{market_context}"
    if context:
        context_lines = "\n".join(f"- {k}: {v}" for k, v in context.items())
        base += f"\n\n## Company Context\n{context_lines}"
    return base
