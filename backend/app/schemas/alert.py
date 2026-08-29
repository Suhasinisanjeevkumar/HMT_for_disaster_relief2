from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AlertOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    claim_id: int
    created_at: datetime
    level: str
    reason_text: str
    acknowledged: bool


class AlertListResponse(BaseModel):
    total: int
    items: list[AlertOut]
