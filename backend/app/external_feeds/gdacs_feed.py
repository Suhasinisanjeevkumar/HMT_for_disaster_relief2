"""
GDACS (Global Disaster Alert and Coordination System) RSS feed -- real,
public domain, no API key. Parsed with the stdlib
xml.etree.ElementTree (no new dependency needed for a ~1.4MB RSS file).

Schema verified directly against the live feed while building this --
GDACS uses namespaced elements (geo:Point/geo:lat/geo:long for
coordinates, gdacs:eventtype/gdacs:country/gdacs:severity for the fields
this project actually needs).
"""
import logging
from datetime import datetime
from email.utils import parsedate_to_datetime
from xml.etree import ElementTree as ET

import requests

from app.external_feeds.base import ExternalEvent, ExternalFeedSource
from app.external_feeds.feed_status import registry

logger = logging.getLogger(__name__)

FEED_URL = "https://www.gdacs.org/xml/rss.xml"

NS = {
    "geo": "http://www.w3.org/2003/01/geo/wgs84_pos#",
    "gdacs": "http://www.gdacs.org",
}

# GDACS event-type codes -> this project's disaster categories (see
# src/disaster/disaster_classifier.py's DISASTER_KEYWORDS). "VO" (volcano)
# has no matching category in this project and is intentionally mapped to
# "Other" rather than silently added as a 14th disaster type -- that
# inventory is a deliberate, spec-scoped decision, not an oversight.
GDACS_TYPE_MAP = {
    "EQ": "Earthquake",
    "TC": "Cyclone",
    "FL": "Flood",
    "DR": "Drought",
    "WF": "Wildfire",
    "VO": "Other",  # volcano -- no matching category, see module docstring
}


def _parse_item(item: ET.Element) -> ExternalEvent | None:
    eventtype_el = item.find("gdacs:eventtype", NS)
    country_el = item.find("gdacs:country", NS)
    severity_el = item.find("gdacs:severity", NS)
    point = item.find("geo:Point", NS)
    lat_el = point.find("geo:lat", NS) if point is not None else None
    lon_el = point.find("geo:long", NS) if point is not None else None
    title_el = item.find("title")
    link_el = item.find("link")
    desc_el = item.find("description")
    pubdate_el = item.find("pubDate")

    if lat_el is None or lon_el is None or title_el is None:
        return None

    raw_type = (eventtype_el.text or "").strip().upper() if eventtype_el is not None else ""
    event_timestamp = None
    if pubdate_el is not None and pubdate_el.text:
        try:
            event_timestamp = parsedate_to_datetime(pubdate_el.text)
        except (TypeError, ValueError):
            event_timestamp = None

    return ExternalEvent(
        source="GDACS",
        event_type=GDACS_TYPE_MAP.get(raw_type, "Other"),
        title=title_el.text or "",
        description=desc_el.text if desc_el is not None else (title_el.text or ""),
        url=link_el.text if link_el is not None else None,
        country=country_el.text if country_el is not None else None,
        latitude=float(lat_el.text),
        longitude=float(lon_el.text),
        event_timestamp=event_timestamp,
        raw_severity=severity_el.text if severity_el is not None else None,
    )


class GDACSFeedSource(ExternalFeedSource):
    name = "GDACS"

    def fetch(self) -> list[ExternalEvent]:
        try:
            resp = requests.get(FEED_URL, timeout=15)
            resp.raise_for_status()
            root = ET.fromstring(resp.content)
        except (requests.RequestException, ET.ParseError) as e:
            logger.warning("GDACS feed fetch failed: %s", e)
            registry.record_error(self.name, str(e))
            return []

        events: list[ExternalEvent] = []
        for item in root.findall(".//item"):
            try:
                event = _parse_item(item)
                if event is not None:
                    events.append(event)
            except (ValueError, TypeError) as e:
                logger.warning("GDACS feed: skipping malformed item: %s", e)
                continue

        registry.record_success(self.name, len(events))
        return events
