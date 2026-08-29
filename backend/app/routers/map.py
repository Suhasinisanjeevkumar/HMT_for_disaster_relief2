from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Claim, Location
from app.db.session import get_db
from app.schemas.map import MapPoint

router = APIRouter(prefix="/api/map", tags=["map"])


@router.get("/claims", response_model=list[MapPoint])
def map_claims(
    db: Session = Depends(get_db),
    disaster_type: str | None = Query(None),
    priority: str | None = Query(None),
    limit: int = Query(1000, ge=1, le=5000),
):
    """Only claims with a resolved (city- or state-centroid) coordinate --
    see src/location/geocode_lookup.py for the permanent precision
    limitation. Returns the PRIMARY location per claim only, to avoid
    plotting the same claim multiple times for multi-location text."""
    stmt = (
        select(Claim, Location)
        .join(Location, Location.claim_id == Claim.id)
        .where(Location.is_primary.is_(True), Location.latitude.is_not(None))
    )
    if disaster_type:
        stmt = stmt.where(Claim.disaster_type == disaster_type)
    if priority:
        stmt = stmt.where(Claim.priority == priority.upper())
    stmt = stmt.limit(limit)

    rows = db.execute(stmt).all()
    return [
        MapPoint(
            claim_id=claim.id,
            latitude=loc.latitude,
            longitude=loc.longitude,
            coordinate_precision=loc.coordinate_precision or "none",
            matched_text=loc.matched_text,
            disaster_type=claim.disaster_type,
            classification=claim.classification,
            priority=claim.priority,
            reliability_band=claim.reliability_band,
            submitted_at=claim.submitted_at,
            is_historical_seed=claim.is_historical_seed,
        )
        for claim, loc in rows
    ]
