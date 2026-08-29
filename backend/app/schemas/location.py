from pydantic import BaseModel, ConfigDict


class LocationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    matched_text: str
    match_level: str
    match_type: str
    locality: str | None
    city: str | None
    district: str | None
    state: str | None
    pin_code: str | None
    latitude: float | None
    longitude: float | None
    coordinate_precision: str | None
    is_primary: bool
