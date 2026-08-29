"""
Matches a claim to recently-fetched external events. Pure functions,
independent of the DB/ORM, so they can be unit-tested with plain
ExternalEvent objects rather than a live database.

A match requires all three:
  (a) topical    -- claim.disaster_type == event.event_type (never matches
                     for "None"/"Other" -- a generic/unclassified claim
                     can't be meaningfully corroborated by a specific
                     event type, and matching everything to "Other" would
                     make this check meaningless)
  (b) geographic -- EITHER a haversine distance under a generous,
                     documented radius from the claim's own resolved
                     coordinates (see src/location/geocode_lookup.py) --
                     100km for a city/locality-level claim location, 300km
                     for district/state-level (Indian states are large;
                     this stays generous on purpose, stated here rather
                     than silently) -- OR, when an event has no
                     coordinates at all (ReliefWeb's list profile doesn't
                     include any, see reliefweb_feed.py), a plain country
                     match as a fallback
  (c) recency    -- the event's timestamp is within RECENCY_DAYS of the
                     claim's submission time. An event with NO timestamp
                     is never matched -- there's no way to bound its
                     recency, so treating it as automatically "recent
                     enough" would be a silent assumption, not a decision.
"""
import math
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from app.external_feeds.base import ExternalEvent

RECENCY_DAYS = 30
RADIUS_KM_BY_LEVEL = {"locality": 100, "city": 100, "district": 300, "state": 300}
DEFAULT_RADIUS_KM = 300


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return 2 * R * math.asin(min(1.0, math.sqrt(a)))


@dataclass
class ClaimGeoContext:
    disaster_type: str
    latitude: Optional[float]
    longitude: Optional[float]
    location_level: Optional[str]
    country_hint: str  # always "India" for this project's gazetteer-resolved claims
    submitted_at: datetime


def _is_recent_enough(event: ExternalEvent, submitted_at: datetime) -> bool:
    if event.event_timestamp is None:
        return False
    age = abs((submitted_at - event.event_timestamp).total_seconds()) / 86400
    return age <= RECENCY_DAYS


def _is_geographically_relevant(event: ExternalEvent, ctx: ClaimGeoContext) -> bool:
    if event.latitude is not None and event.longitude is not None and ctx.latitude is not None and ctx.longitude is not None:
        radius = RADIUS_KM_BY_LEVEL.get(ctx.location_level, DEFAULT_RADIUS_KM)
        return haversine_km(ctx.latitude, ctx.longitude, event.latitude, event.longitude) <= radius
    if event.country:
        return event.country.strip().lower() == ctx.country_hint.strip().lower()
    return False


def find_matches(ctx: ClaimGeoContext, events: list[ExternalEvent], require_type: bool = True) -> list[ExternalEvent]:
    """With require_type=True (the normal case -- these are the events
    that actually corroborate the claim and become Evidence rows):
    matches must be the SAME disaster type as the claim.

    With require_type=False: ignores the type filter entirely, used only
    to answer a different question -- "did anything geographically/
    recency-relevant happen here at all, regardless of type?" This is
    what lets reliability_scorer distinguish "no evidence exists nearby"
    (nothing found either way) from "evidence exists nearby, but for a
    different disaster type" (found here, empty with require_type=True) --
    see pipeline_service.py's evidence_type_matches logic."""
    if require_type and ctx.disaster_type in (None, "None", "Other"):
        return []
    matches = []
    for event in events:
        if require_type and event.event_type != ctx.disaster_type:
            continue
        if not _is_recent_enough(event, ctx.submitted_at):
            continue
        if not _is_geographically_relevant(event, ctx):
            continue
        matches.append(event)
    return matches
