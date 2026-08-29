from fastapi import APIRouter

from app.external_feeds.feed_status import registry
from app.external_feeds.scheduler import refresh_all
from app.schemas.feed import FeedHealthOut

router = APIRouter(prefix="/api/feeds", tags=["feeds"])


@router.get("/status", response_model=list[FeedHealthOut])
def feed_status():
    """Per-source health for all real (USGS/GDACS/ReliefWeb) and stub
    (NewsAPI/GoogleFactCheck/Reddit/Telegram) sources -- "not_configured"
    and "error" are deliberately distinct statuses, see feed_status.py."""
    return registry.all()


@router.post("/refresh")
def trigger_refresh():
    """On-demand refresh, useful for demos/tests without waiting for the
    15-minute background interval (see scheduler.py)."""
    events = refresh_all()
    return {"fetched_event_count": len(events)}
