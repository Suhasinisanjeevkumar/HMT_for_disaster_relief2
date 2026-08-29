import logging

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.models import Claim, Location
from app.schemas.claim import ClaimCreate, ClaimDetail, ClaimListResponse
from app.services.pipeline_service import analyze_and_persist

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/claims", tags=["claims"])


@router.post("", response_model=ClaimDetail, status_code=201)
def create_claim(payload: ClaimCreate, db: Session = Depends(get_db)):
    try:
        claim = analyze_and_persist(db, payload.text, payload.source, payload.source_url)
    except Exception:
        # The analysis pipeline (model loading, gazetteer lookup, etc.) is
        # external-ish machinery from the API's point of view -- never leak
        # a raw stack trace to the client, but do log it for debugging.
        logger.exception("claim analysis failed for submitted text")
        raise HTTPException(status_code=500, detail="Claim analysis failed. See server logs.")
    return claim


@router.get("", response_model=ClaimListResponse)
def list_claims(
    db: Session = Depends(get_db),
    verdict: str | None = Query(None, description="TRUE | FAKE | UNVERIFIED"),
    disaster_type: str | None = None,
    priority: str | None = Query(None, description="HIGH | MEDIUM | LOW"),
    state: str | None = None,
    q: str | None = Query(None, description="substring search over claim text"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    stmt = select(Claim)
    if verdict:
        stmt = stmt.where(Claim.classification == verdict.upper())
    if disaster_type:
        stmt = stmt.where(Claim.disaster_type == disaster_type)
    if priority:
        stmt = stmt.where(Claim.priority == priority.upper())
    if q:
        stmt = stmt.where(Claim.text.ilike(f"%{q}%"))
    if state:
        stmt = stmt.join(Location).where(Location.state == state)

    total = db.scalar(select(func.count()).select_from(stmt.subquery()))
    stmt = stmt.order_by(Claim.submitted_at.desc()).limit(limit).offset(offset)
    items = db.scalars(stmt).unique().all()
    return ClaimListResponse(total=total or 0, items=items)


@router.get("/{claim_id}", response_model=ClaimDetail)
def get_claim(claim_id: int, db: Session = Depends(get_db)):
    claim = db.get(Claim, claim_id)
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")
    return claim
