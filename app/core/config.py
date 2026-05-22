from __future__ import annotations
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env for local development. On Railway this file doesn't exist and
# load_dotenv() silently does nothing — env vars come from Railway's Variables.
load_dotenv(Path(__file__).parent.parent.parent / ".env")


class Settings:
    anthropic_api_key: str = os.environ.get("ANTHROPIC_API_KEY", "")
    claude_model: str = os.environ.get("CLAUDE_MODEL", "claude-sonnet-4-6")
    max_tokens: int = int(os.environ.get("MAX_TOKENS", "2048"))
    app_name: str = "fund-lens"
    debug: bool = os.environ.get("DEBUG", "false").lower() == "true"
    tavily_api_key: str | None = os.environ.get("TAVILY_API_KEY") or None


settings = Settings()

if not settings.anthropic_api_key:
    raise RuntimeError(
        "ANTHROPIC_API_KEY is not set.\n"
        "  • Railway: add it in the service Variables tab\n"
        "  • Local:   add it to your .env file"
    )
