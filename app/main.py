from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from app.core.config import settings
from app.routers import analyze, ask, portfolio
from app.services import market_data

_STATIC = Path(__file__).parent / "static"

_DESCRIPTION = """
**fund-lens** is an AI-powered financial analysis API built for PE (private equity) sponsors
and CFO teams. It connects to Claude (Anthropic's AI) and turns raw financial metrics into
structured, actionable analyst-quality commentary — in seconds.

---

## What it does

| Endpoint | What you send | What you get back |
|---|---|---|
| `POST /analyze` | One company's financial metrics | Narrative analysis, key insights, risk flags, and recommendations |
| `POST /ask` | A freeform CFO question (+ optional history) | A conversational answer; supports multi-turn follow-ups |
| `POST /portfolio/compare` | Metrics for two companies | Side-by-side comparison with a category-by-category verdict |
| `GET /health` | Nothing | Server status and active model |

---

## Who it's for

- **PE sponsors** who want a quick read on portfolio company health without pulling up a model
- **CFOs** who want on-demand answers to finance questions grounded in their own numbers
- **Analysts** who want a first-pass narrative they can refine, rather than writing from scratch

---

## Key concepts

- All AI calls go through **Claude** via the Anthropic API — you need an `ANTHROPIC_API_KEY` in `.env`
- `/ask` supports **multi-turn conversations**: pass the `updated_history` from each response
  back as `conversation_history` in the next request to maintain context
- All inputs are validated by **Pydantic** — invalid or missing fields return a `422` with a clear error before Claude is ever called
"""

_TAGS = [
    {
        "name": "Analysis",
        "description": "Analyze a single company's financial metrics and receive a structured AI-generated assessment.",
    },
    {
        "name": "Ask",
        "description": (
            "Ask freeform CFO questions in natural language. Supports multi-turn conversations — "
            "pass `updated_history` from each response back as `conversation_history` to continue the thread."
        ),
    },
    {
        "name": "Portfolio",
        "description": "Compare two portfolio companies side-by-side across growth, profitability, and financial health.",
    },
    {
        "name": "System",
        "description": "Health and status endpoints.",
    },
]

app = FastAPI(
    title="fund-lens",
    description=_DESCRIPTION,
    version="0.1.0",
    openapi_tags=_TAGS,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.include_router(analyze.router)
app.include_router(ask.router)
app.include_router(portfolio.router)
app.mount("/static", StaticFiles(directory=_STATIC), name="static")

@app.get("/", response_class=FileResponse, include_in_schema=False)
async def landing() -> FileResponse:
    return FileResponse(_STATIC / "index.html")


@app.get("/health", tags=["System"], summary="Health check")
async def health() -> dict:
    """Returns server status and the active Claude model name."""
    return {"status": "ok", "model": settings.claude_model}


@app.get("/market-context", tags=["System"], summary="Live market data injected into prompts")
async def get_market_context() -> dict:
    """
    Returns the live market data block that is currently being injected into every Claude prompt.
    Useful for verifying that real-time data is flowing correctly.
    Data is cached for 15 minutes — this endpoint always reflects the cached value.
    """
    context = await market_data.get_market_context(settings.tavily_api_key)
    return {
        "market_context": context,
        "tavily_enabled": bool(settings.tavily_api_key),
        "cache_ttl_seconds": 900,
    }
