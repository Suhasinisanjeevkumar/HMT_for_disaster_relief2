"""
USGS significant-earthquakes feed -- real, no API key, no signup.

Endpoint verified directly against the live feed while building this
(the commonly-guessed "/earthquake/feed/..." URL 404s -- the real path
is plural, "/earthquakes/feed/...").
"""
import logging
from datetime import datetime, timezone

import requests

from app.external_feeds.base import ExternalEvent, ExternalFeedSource
from app.external_feeds.feed_status import registry

logger = logging.getLogger(__name__)

FEED_URL = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/significant_week.geojson"

# Deliberately a South Asia regional box, not a tight India-only box:
# lat 6-38, lon 68-98 also covers Nepal, Bangladesh, Bhutan, and parts of
# Pakistan/Myanmar/China near the border. Confirmed empirically while
# building this (a real "Nepal" event fell inside this box) -- kept
# intentionally generous because a border-region disaster (e.g. a Nepal
# earthquake affecting Bihar/UP) is genuinely relevant evidence for
# India-focused disaster relief, not noise. evidence_matcher.py applies
# the real per-claim distance filter on top of this; this box only limits
# how much of the global feed gets fetched into memory at all.
LAT_MIN, LAT_MAX = 6.0, 38.0
LON_MIN, LON_MAX = 68.0, 98.0

USGS_TYPE_MAP = {
    "earthquake": "Earthquake",
    "landslide": "Landslide",
}


def _in_region(lat: float, lon: float) -> bool:
    return LAT_MIN <= lat <= LAT_MAX and LON_MIN <= lon <= LON_MAX


class USGSFeedSource(ExternalFeedSource):
    name = "USGS"

    def fetch(self) -> list[ExternalEvent]:
        try:
            resp = requests.get(FEED_URL, timeout=10)
            resp.raise_for_status()
            data = resp.json()
        except (requests.RequestException, ValueError) as e:
            logger.warning("USGS feed fetch failed: %s", e)
            registry.record_error(self.name, str(e))
            return []

        events = []
        for feature in data.get("features", []):
            try:
                props = feature["properties"]
                lon, lat = feature["geometry"]["coordinates"][:2]
                if not _in_region(lat, lon):
                    continue
                raw_type = (props.get("type") or "earthquake").lower()
                events.append(
                    ExternalEvent(
                        source=self.name,
                        event_type=USGS_TYPE_MAP.get(raw_type, "Other"),
                        title=props.get("title") or f"M{props.get('mag')} event",
                        description=f"{props.get('title')} -- {props.get('place')}",
                        url=props.get("url"),
                        country=None,  # USGS doesn't give a country field, only a free-text "place"
                        latitude=lat,
                        longitude=lon,
                        event_timestamp=(
                            datetime.fromtimestamp(props["time"] / 1000, tz=timezone.utc)
                            if props.get("time") else None
                        ),
                        raw_severity=f"M{props.get('mag')}" if props.get("mag") is not None else None,
                    )
                )
            except (KeyError, TypeError, IndexError) as e:
                logger.warning("USGS feed: skipping malformed feature: %s", e)
                continue

        registry.record_success(self.name, len(events))
        return events
