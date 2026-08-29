from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.models import Claim, Location
from app.db.session import get_db
from app.schemas.stats import CountItem, OverviewStats, TimelinePoint

router = APIRouter(prefix="/api/stats", tags=["stats"])


@router.get("/overview", response_model=OverviewStats)
def overview(db: Session = Depends(get_db)):
    total = db.scalar(select(func.count()).select_from(Claim)) or 0
    true_count = db.scalar(select(func.count()).where(Claim.classification == "TRUE")) or 0
    fake_count = db.scalar(select(func.count()).where(Claim.classification == "FAKE")) or 0
    unverified_count = db.scalar(select(func.count()).where(Claim.classification == "UNVERIFIED")) or 0
    high_priority_count = db.scalar(select(func.count()).where(Claim.priority == "HIGH")) or 0
    verified_count = db.scalar(select(func.count()).where(Claim.verification_status == "matched")) or 0

    return OverviewStats(
        total_claims=total,
        true_count=true_count,
        fake_count=fake_count,
        unverified_count=unverified_count,
        high_priority_count=high_priority_count,
        verified_against_corpus_count=verified_count,
        verification_rate=(verified_count / total) if total else 0.0,
    )


@router.get("/disaster-types", response_model=list[CountItem])
def disaster_type_breakdown(db: Session = Depends(get_db)):
    rows = db.execute(
        select(Claim.disaster_type, func.count()).group_by(Claim.disaster_type).order_by(func.count().desc())
    ).all()
    return [CountItem(label=label, count=count) for label, count in rows]


@router.get("/locations", response_model=list[CountItem])
def top_locations(
    db: Session = Depends(get_db),
    by: str = Query("state", pattern="^(state|city)$"),
    limit: int = Query(15, ge=1, le=50),
):
    column = Location.state if by == "state" else Location.city
    rows = db.execute(
        select(column, func.count())
        .where(Location.is_primary.is_(True), column.is_not(None))
        .group_by(column)
        .order_by(func.count().desc())
        .limit(limit)
    ).all()
    return [CountItem(label=label, count=count) for label, count in rows]


@router.get("/timeline", response_model=list[TimelinePoint])
def timeline(db: Session = Depends(get_db)):
    day = func.date(Claim.submitted_at)
    rows = db.execute(select(day, func.count()).group_by(day).order_by(day)).all()
    return [TimelinePoint(date=str(d), count=c) for d, c in rows]
