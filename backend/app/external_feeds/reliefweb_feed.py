"""
ReliefWeb (UN OCHA) disasters API.

HONEST CORRECTION vs. the original plan for this module: ReliefWeb was
planned as a third "no key, no signup" source alongside USGS and GDACS.
Verified directly against the live API while building this, and that
turned out to be wrong -- ReliefWeb's v1 API is fully decommissioned
(HTTP 410), and v2 requires an *approved* `appname`, not just any string:
an arbitrary appname gets a 403 "You are not using an approved appname"
response with a link to request one (https://apidoc.reliefweb.int/parameters#appname).

So this source is real, working code -- the request/parsing logic below
is correct and tested against ReliefWeb's documented response shape via
mocks -- but it is NOT currently active, because no approved appname has
been obtained (same underlying situation as the NewsAPI/Google Fact
Check/Reddit/Telegram stubs in stub_feeds.py, just discovered emprically
rather than assumed up front). A 403 specifically matching ReliefWeb's
"not an approved appname" message is reported as feed status
"not_configured", not "error", so it's clearly distinguished in
/api/feeds/status and the About page from a transient outage. See
DATA_SOURCES.md and STATUS.md for the full account of this finding.
"""
import logging
from datetime import datetime, timezone

import requests

from app.config import settings
from app.external_feeds.base import ExternalEvent, ExternalFeedSource
from app.external_feeds.feed_status import registry

logger = logging.getLogger(__name__)

API_URL = "https://api.reliefweb.int/v2/disasters"

# ReliefWeb's own disaster "type" names -> this project's disaster
# categories. Anything not in this map (e.g. "Epidemic", "Cold Wave",
# "Complex Emergency") is intentionally left as "Other" rather than
# expanding the disaster-type inventory (a deliberate, spec-scoped
# decision -- see src/disaster/disaster_classifier.py).
RELIEFWEB_TYPE_MAP = {
    "Flood": "Flood",
    "Flash Flood": "Flood",
    "Tropical Cyclone": "Cyclone",
    "Earthquake": "Earthquake",
    "Land Slide": "Landslide",
    "Drought": "Drought",
    "Wild Fire": "Wildfire",
    "Tsunami": "Tsunami",
    "Storm": "Storm",
}

_NOT_APPROVED_MARKER = "not using an approved appname"


class ReliefWebFeedSource(ExternalFeedSource):
    name = "ReliefWeb"

    def fetch(self) -> list[ExternalEvent]:
        params = {
            "appname": settings.reliefweb_appname,
            "profile": "list",
            "filter[field]": "country",
            "filter[value]": "India",
            "limit": 20,
            "sort[]": "date.created:desc",
        }
        try:
            resp = requests.get(API_URL, params=params, timeout=10)
            if resp.status_code == 403 and _NOT_APPROVED_MARKER in resp.text:
                registry.record_not_configured(
                    self.name,
                    "ReliefWeb appname not approved -- request one at "
                    "https://apidoc.reliefweb.int/parameters#appname",
                )
                return []
            resp.raise_for_status()
            data = resp.json()
        except (requests.RequestException, ValueError) as e:
            logger.warning("ReliefWeb feed fetch failed: %s", e)
            registry.record_error(self.name, str(e))
            return []

        events = []
        for item in data.get("data", []):
            try:
                fields = item["fields"]
                type_names = [t.get("name") for t in fields.get("type", [])]
                mapped_type = next(
                    (RELIEFWEB_TYPE_MAP[t] for t in type_names if t in RELIEFWEB_TYPE_MAP), "Other"
                )
                event_date = fields.get("date", {}).get("event") or fields.get("date", {}).get("created")
                events.append(
                    ExternalEvent(
                        source=self.name,
                        event_type=mapped_type,
                        title=fields.get("name", ""),
                        description=fields.get("description", "") or fields.get("name", ""),
                        url=fields.get("url"),
                        country="India",
                        latitude=None,  # ReliefWeb's disaster list profile doesn't include coordinates
                        longitude=None,
                        event_timestamp=(
                            datetime.fromisoformat(event_date.replace("Z", "+00:00"))
                            if event_date else None
                        ),
                        raw_severity=fields.get("status"),
                    )
                )
            except (KeyError, TypeError, ValueError) as e:
                logger.warning("ReliefWeb feed: skipping malformed item: %s", e)
                continue

        registry.record_success(self.name, len(events))
        return events
