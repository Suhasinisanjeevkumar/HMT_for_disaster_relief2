from datetime import datetime

from pydantic import BaseModel, ConfigDict


class FeedHealthOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    status: str  # "ok" | "error" | "not_configured" | "unknown"
    last_attempt_at: datetime | None
    last_success_at: datetime | None
    last_error: str | None
    last_event_count: int
