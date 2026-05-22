"""
Fetches live market data to inject into Claude prompts as grounding context.
Results are cached for 15 minutes so external APIs aren't hit on every request.
"""
from __future__ import annotations

import asyncio
import time
from typing import Optional

import httpx

_cache: dict = {}
_CACHE_TTL = 900  # 15 minutes


def _sync_fetch_rates_and_indices() -> dict:
    """Runs in a thread pool — yfinance is synchronous."""
    try:
        import yfinance as yf
    except ImportError:
        return {}

    data: dict = {}

    # Interest rates
    for symbol, key in [
        ("^TNX", "treasury_10y"),
        ("^IRX", "t_bill_13wk"),
        ("^VIX", "vix"),
    ]:
        try:
            hist = yf.Ticker(symbol).history(period="5d")
            if not hist.empty:
                data[key] = round(float(hist["Close"].iloc[-1]), 2)
        except Exception:
            continue

    # S&P 500 one-month return
    try:
        hist = yf.Ticker("SPY").history(period="1mo")
        if len(hist) >= 2:
            ret = (hist["Close"].iloc[-1] / hist["Close"].iloc[0] - 1) * 100
            data["sp500_1mo_pct"] = round(float(ret), 1)
    except Exception:
        pass

    # Median EV/Revenue from a small basket of public SaaS companies
    ev_revs: list[float] = []
    for sym in ["CRM", "DDOG", "NET", "ZS"]:
        try:
            info = yf.Ticker(sym).info
            ev_rev = info.get("enterpriseToRevenue")
            if ev_rev and float(ev_rev) > 0:
                ev_revs.append(float(ev_rev))
        except Exception:
            continue
    if ev_revs:
        ev_revs.sort()
        mid = len(ev_revs) // 2
        median = ev_revs[mid] if len(ev_revs) % 2 else (ev_revs[mid - 1] + ev_revs[mid]) / 2
        data["saas_median_ev_rev"] = round(median, 1)
        data["saas_basket"] = "CRM, DDOG, NET, ZS"

    return data


async def _fetch_tavily_snippets(api_key: str) -> list[str]:
    """Returns a few short news snippets relevant to PE/VC market conditions."""
    queries = [
        "private equity M&A deal activity market conditions 2025",
        "SaaS valuation multiples venture capital fundraising 2025",
    ]
    snippets: list[str] = []
    async with httpx.AsyncClient(timeout=10) as client:
        for query in queries:
            try:
                resp = await client.post(
                    "https://api.tavily.com/search",
                    json={
                        "api_key": api_key,
                        "query": query,
                        "search_depth": "basic",
                        "max_results": 3,
                        "include_answer": True,
                    },
                )
                body = resp.json()
                if body.get("answer"):
                    snippets.append(body["answer"])
                for r in body.get("results", [])[:2]:
                    content = (r.get("content") or "").strip()
                    title = r.get("title", "")
                    if content:
                        snippets.append(f"[{title}] {content[:300]}")
            except Exception:
                continue
    return snippets


async def get_market_context(tavily_api_key: Optional[str] = None) -> str:
    """
    Returns a formatted market-context block for injection into Claude prompts.
    Cached for 15 minutes; silently degrades if external services are unavailable.
    """
    now = time.time()
    cached = _cache.get("ctx")
    if cached and now - cached["ts"] < _CACHE_TTL:
        return cached["value"]

    loop = asyncio.get_event_loop()

    # Run yfinance (sync) and optional Tavily (async) in parallel
    tasks: list = [loop.run_in_executor(None, _sync_fetch_rates_and_indices)]
    if tavily_api_key:
        tasks.append(_fetch_tavily_snippets(tavily_api_key))

    results = await asyncio.gather(*tasks, return_exceptions=True)

    mkt: dict = results[0] if isinstance(results[0], dict) else {}
    news: list[str] = results[1] if len(results) > 1 and isinstance(results[1], list) else []

    lines: list[str] = []

    # ── Rates & macro ──────────────────────────────────────────────
    rate_lines: list[str] = []
    if mkt.get("treasury_10y"):
        rate_lines.append(f"10-Year Treasury Yield: {mkt['treasury_10y']}%")
    if mkt.get("t_bill_13wk"):
        rate_lines.append(f"13-Week T-Bill (short-term rate proxy): {mkt['t_bill_13wk']}%")
    if rate_lines:
        lines.append("## Live Interest Rates")
        lines.extend(f"- {l}" for l in rate_lines)

    # ── Market sentiment ───────────────────────────────────────────
    sentiment_lines: list[str] = []
    if mkt.get("vix") is not None:
        v = mkt["vix"]
        mood = "elevated — risk-off environment" if v > 25 else "moderate" if v > 15 else "low — risk-on environment"
        sentiment_lines.append(f"VIX (equity volatility index): {v} ({mood})")
    if mkt.get("sp500_1mo_pct") is not None:
        r = mkt["sp500_1mo_pct"]
        sentiment_lines.append(f"S&P 500 past 30 days: {r:+.1f}%")
    if sentiment_lines:
        lines.append("\n## Live Market Sentiment")
        lines.extend(f"- {l}" for l in sentiment_lines)

    # ── Public SaaS multiples ──────────────────────────────────────
    if mkt.get("saas_median_ev_rev"):
        lines.append(f"\n## Live Public SaaS Valuation Benchmark")
        lines.append(
            f"- Median EV/Revenue ({mkt['saas_basket']}): {mkt['saas_median_ev_rev']}x"
        )
        lines.append(
            "  (Use as a rough public-market anchor; private-company discounts of 20–40% are typical)"
        )

    # ── Recent news ────────────────────────────────────────────────
    if news:
        lines.append("\n## Recent PE/VC Market News (via Tavily)")
        for snippet in news[:4]:
            lines.append(f"- {snippet}")

    result = "\n".join(lines) if lines else ""
    _cache["ctx"] = {"ts": now, "value": result}
    return result
