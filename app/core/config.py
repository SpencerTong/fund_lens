import os
import sys
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings

# Only load .env file if it actually exists (locally). On Railway and other
# cloud platforms there is no .env file — env vars are injected directly into
# the process and must be read from os.environ, not from a file.
_env_file = ".env" if Path(".env").exists() else None


class Settings(BaseSettings):
    anthropic_api_key: str
    claude_model: str = "claude-sonnet-4-6"
    max_tokens: int = 2048
    app_name: str = "fund-lens"
    debug: bool = False
    tavily_api_key: Optional[str] = None

    model_config = {"env_file": _env_file, "env_file_encoding": "utf-8"}


# Emit a clear startup log so Railway's deployment logs show exactly which
# required variables are present or missing — visible under "Deployments → logs".
_required = {"ANTHROPIC_API_KEY"}
_found = _required & set(os.environ)
_missing = _required - _found
if _missing:
    print(
        f"[fund-lens] STARTUP ERROR — missing required env vars: {sorted(_missing)}\n"
        f"[fund-lens] Variables visible in os.environ: {sorted(k for k in os.environ if not k.startswith('_'))}",
        file=sys.stderr,
        flush=True,
    )

settings = Settings()
