import pytest

from app.external_feeds.base import FeedNotConfiguredError
from app.external_feeds.stub_feeds import NewsAPIFeedSource, RedditFeedSource


def test_newsapi_missing_key_raises_named_error(monkeypatch):
    monkeypatch.setattr("app.external_feeds.stub_feeds.settings.news_api_key", None)
    with pytest.raises(FeedNotConfiguredError, match="NEWS_API_KEY"):
        NewsAPIFeedSource().fetch()


def test_reddit_missing_credentials_raises_named_error(monkeypatch):
    monkeypatch.setattr("app.external_feeds.stub_feeds.settings.reddit_client_id", None)
    monkeypatch.setattr("app.external_feeds.stub_feeds.settings.reddit_client_secret", None)
    with pytest.raises(FeedNotConfiguredError, match="REDDIT_CLIENT_ID"):
        RedditFeedSource().fetch()
