from unittest.mock import patch, MagicMock

from app.external_feeds.usgs_feed import USGSFeedSource
from app.external_feeds.gdacs_feed import GDACSFeedSource
from app.external_feeds.reliefweb_feed import ReliefWebFeedSource

USGS_SAMPLE = {
    "features": [
        {
            "properties": {
                "mag": 5.2, "place": "50 km NW of Kathmandu, Nepal", "time": 1735689600000,
                "url": "https://example.com/eq1", "type": "earthquake",
            },
            "geometry": {"type": "Point", "coordinates": [85.3, 27.7, 10]},
        },
        {
            # outside the South Asia bounding box -- should be filtered out
            "properties": {"mag": 6.1, "place": "Tokyo, Japan", "time": 1735689600000, "url": "x", "type": "earthquake"},
            "geometry": {"type": "Point", "coordinates": [139.7, 35.7, 10]},
        },
    ]
}

GDACS_SAMPLE_XML = b"""<?xml version="1.0" encoding="utf-8"?>
<rss xmlns:geo="http://www.w3.org/2003/01/geo/wgs84_pos#" xmlns:gdacs="http://www.gdacs.org">
  <channel>
    <item>
      <title>Orange flood alert in India</title>
      <description>A flood in India.</description>
      <link>https://www.gdacs.org/report.aspx?eventid=1</link>
      <pubDate>Fri, 28 Aug 2026 05:32:14 GMT</pubDate>
      <geo:Point><geo:lat>25.33</geo:lat><geo:long>83.00</geo:long></geo:Point>
      <gdacs:eventtype>FL</gdacs:eventtype>
      <gdacs:country>India</gdacs:country>
      <gdacs:severity unit="M" value="0">Flood</gdacs:severity>
    </item>
  </channel>
</rss>"""


def test_usgs_parses_wellformed_payload_and_filters_by_region():
    with patch("app.external_feeds.usgs_feed.requests.get") as mock_get:
        mock_get.return_value = MagicMock(status_code=200, json=lambda: USGS_SAMPLE)
        mock_get.return_value.raise_for_status = lambda: None
        events = USGSFeedSource().fetch()
    assert len(events) == 1
    assert events[0].event_type == "Earthquake"


def test_usgs_timeout_returns_empty_list_without_raising():
    import requests
    with patch("app.external_feeds.usgs_feed.requests.get", side_effect=requests.Timeout("timed out")):
        events = USGSFeedSource().fetch()
    assert events == []


def test_usgs_malformed_payload_returns_empty_list():
    with patch("app.external_feeds.usgs_feed.requests.get") as mock_get:
        mock_get.return_value = MagicMock(status_code=200, json=lambda: {"not": "a valid shape"})
        mock_get.return_value.raise_for_status = lambda: None
        events = USGSFeedSource().fetch()
    assert events == []


def test_gdacs_parses_wellformed_payload():
    with patch("app.external_feeds.gdacs_feed.requests.get") as mock_get:
        mock_get.return_value = MagicMock(status_code=200, content=GDACS_SAMPLE_XML)
        mock_get.return_value.raise_for_status = lambda: None
        events = GDACSFeedSource().fetch()
    assert len(events) == 1
    assert events[0].event_type == "Flood"
    assert events[0].country == "India"


def test_gdacs_connection_error_returns_empty_list():
    import requests
    with patch("app.external_feeds.gdacs_feed.requests.get", side_effect=requests.ConnectionError("down")):
        events = GDACSFeedSource().fetch()
    assert events == []


def test_reliefweb_unapproved_appname_is_not_configured_not_error():
    resp = MagicMock(status_code=403, text="You are not using an approved appname")
    with patch("app.external_feeds.reliefweb_feed.requests.get", return_value=resp):
        events = ReliefWebFeedSource().fetch()
    assert events == []
