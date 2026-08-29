from datetime import datetime, timedelta, timezone

from app.external_feeds.base import ExternalEvent
from app.external_feeds.evidence_matcher import ClaimGeoContext, find_matches

NOW = datetime(2026, 8, 29, tzinfo=timezone.utc)


def _flood_event(lat=25.3, lon=83.0, event_type="Flood", days_ago=5, country="India"):
    return ExternalEvent(
        source="GDACS", event_type=event_type, title="t", description="d", url=None,
        country=country, latitude=lat, longitude=lon,
        event_timestamp=NOW - timedelta(days=days_ago),
    )


def test_matching_type_geo_and_recency_matches():
    ctx = ClaimGeoContext(
        disaster_type="Flood", latitude=25.3, longitude=83.0,
        location_level="city", country_hint="India", submitted_at=NOW,
    )
    matches = find_matches(ctx, [_flood_event()])
    assert len(matches) == 1


def test_wrong_disaster_type_does_not_match():
    ctx = ClaimGeoContext(
        disaster_type="Earthquake", latitude=25.3, longitude=83.0,
        location_level="city", country_hint="India", submitted_at=NOW,
    )
    matches = find_matches(ctx, [_flood_event()])
    assert matches == []


def test_stale_event_does_not_match():
    ctx = ClaimGeoContext(
        disaster_type="Flood", latitude=25.3, longitude=83.0,
        location_level="city", country_hint="India", submitted_at=NOW,
    )
    matches = find_matches(ctx, [_flood_event(days_ago=90)])
    assert matches == []


def test_no_coordinates_falls_back_to_country_match():
    ctx = ClaimGeoContext(
        disaster_type="Flood", latitude=25.3, longitude=83.0,
        location_level="city", country_hint="India", submitted_at=NOW,
    )
    event = _flood_event(lat=None, lon=None)
    matches = find_matches(ctx, [event])
    assert len(matches) == 1
