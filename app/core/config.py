from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    anthropic_api_key: str
    claude_model: str = "claude-sonnet-4-6"
    max_tokens: int = 2048
    app_name: str = "fund-lens"
    debug: bool = False
    # Optional — enables live PE/VC news and SaaS multiple search
    tavily_api_key: Optional[str] = None

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
