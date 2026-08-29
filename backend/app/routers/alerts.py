from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.models import Alert
from app.db.session import get_db
from app.schemas.alert import AlertListResponse, AlertOut

router = APIRouter(prefix="/api/alerts", tags=["alerts"])


@router.get("", response_model=AlertListResponse)
def list_alerts(
    db: Session = Depends(get_db),
    acknowledged: bool | None = Query(None),
    level: str | None = Query(None, description="HIGH | MEDIUM | LOW"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    stmt = select(Alert)
    if acknowledged is not None:
        stmt = stmt.where(Alert.acknowledged == acknowledged)
    if level:
        stmt = stmt.where(Alert.level == level.upper())

    total = db.scalar(select(func.count()).select_from(stmt.subquery()))
    stmt = stmt.order_by(Alert.created_at.desc()).limit(limit).offset(offset)
    items = db.scalars(stmt).all()
    return AlertListResponse(total=total or 0, items=items)


@router.patch("/{alert_id}/acknowledge", response_model=AlertOut)
def acknowledge_alert(alert_id: int, db: Session = Depends(get_db)):
    alert = db.get(Alert, alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    alert.acknowledged = True  # idempotent -- setting True on an already-True alert is a no-op
    db.commit()
    db.refresh(alert)
    return alert
