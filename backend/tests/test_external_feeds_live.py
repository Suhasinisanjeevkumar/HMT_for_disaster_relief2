"""
Real network calls against the 3 live-feed endpoints -- confirms today's
actual schema still parses as our fetchers expect. Excluded from the
default `pytest` run (see pytest.ini's `addopts = -m "not network"`) so
CI/offline development never depends on internet access; run explicitly
with `pytest -m network` when you want to check the feeds still work.

ReliefWeb is expected to report "not_configured" (no approved appname --
see DATA_SOURCES.md), not raise and not silently succeed with fake data.
"""
import pytest

from app.external_feeds.usgs_feed import USGSFeedSource
from app.external_feeds.gdacs_feed import GDACSFeedSource
from app.external_feeds.reliefweb_feed import ReliefWebFeedSource
from app.external_feeds.feed_status import registry

pytestmark = pytest.mark.network


def test_usgs_feed_reachable_and_parses():
    events = USGSFeedSource().fetch()
    # Not asserting len > 0 -- "significant" earthquakes near South Asia
    # in the last week is genuinely sometimes zero. Asserting the call
    # succeeded (no exception, status recorded "ok") is the real claim here.
    assert isinstance(events, list)
    statuses = {h.name: h.status for h in registry.all()}
    assert statuses.get("USGS") == "ok"


def test_gdacs_feed_reachable_and_parses():
    events = GDACSFeedSource().fetch()
    assert isinstance(events, list)
    assert len(events) > 0  # GDACS's global feed is never empty


def test_reliefweb_reports_not_configured_not_error():
    events = ReliefWebFeedSource().fetch()
    assert events == []
    statuses = {h.name: h.status for h in registry.all()}
    assert statuses.get("ReliefWeb") == "not_configured"
