"""
Common interface for external evidence sources -- same
one-ABC-one-implementation convention as src/disaster/disaster_classifier.py,
src/location/location_extractor.py, and
src/misinformation/misinformation_classifier.py.

A feed source's job is ONLY to fetch and normalize its provider's data into
ExternalEvent objects. It must NEVER let a network/parsing failure escape
`fetch()` as an exception -- claim analysis has to keep working even if
every external feed is down. See feed_status.py for how failures are
recorded instead.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


class FeedNotConfiguredError(Exception):
    """Raised by a credentialed stub source (see stub_feeds.py) when the
    env var(s) it needs are not set. This is deliberately a DIFFERENT
    exception type/status ("not_configured") than a transient fetch
    failure ("error") -- the two must never be conflated in
    /api/feeds/status or the About page, since one means "no credentials
    exist for this integration" (permanent, by design) and the other
    means "the provider was unreachable just now" (transient)."""


@dataclass
class ExternalEvent:
    source: str            # "USGS" | "ReliefWeb" | "GDACS"
    event_type: str        # mapped to a DISASTER_KEYWORDS category name where possible, else "Other"
    title: str
    description: str
    url: Optional[str]
    country: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    event_timestamp: Optional[datetime]
    raw_severity: Optional[str] = None


class ExternalFeedSource(ABC):
    name: str

    @abstractmethod
    def fetch(self) -> list[ExternalEvent]:
        """Must return [] on any failure -- never raise (FeedNotConfiguredError
        from stub sources is the one deliberate exception to that rule, and
        is caught specifically by the scheduler, not treated as a generic
        error)."""
        raise NotImplementedError
