from datetime import datetime

from pydantic import BaseModel


class MapPoint(BaseModel):
    claim_id: int
    latitude: float
    longitude: float
    coordinate_precision: str
    matched_text: str
    disaster_type: str
    classification: str
    priority: str
    reliability_band: str | None
    submitted_at: datetime
    is_historical_seed: bool
