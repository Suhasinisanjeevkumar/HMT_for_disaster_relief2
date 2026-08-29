"""
Backend configuration -- all values come from environment variables (see
.env.example at the repo root) with safe dev defaults, so the app runs
out of the box on a fresh clone without any secrets configured.

Nothing here should ever be a hardcoded credential. Sources without a
configured key simply stay disabled (see external_feeds/stub_feeds.py) --
that is a deliberate design choice (Module 1 spec item), not an oversight.
"""
import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(__file__), "..", "..", ".env"),
        extra="ignore",
    )

    database_url: str = "sqlite:///./hmt.db"
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    reliefweb_appname: str = "hmt-capstone-project"

    # Future Enhancement -- credentialed sources. None of these have real
    # values in this project (see STATUS.md); their absence is what keeps
    # stub_feeds.py's FeedNotConfiguredError firing, on purpose.
    news_api_key: str | None = None
    google_fact_check_api_key: str | None = None
    reddit_client_id: str | None = None
    reddit_client_secret: str | None = None
    telegram_api_id: str | None = None
    telegram_api_hash: str | None = None

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


settings = Settings()
