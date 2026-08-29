"""
Explicit, env-var-ready stubs for sources that need real credentials this
project does not have (see STATUS.md "What I need from you to keep
going" -- Reddit OAuth, Telegram api_id/api_hash, and a Google Fact Check
Tools API key were never obtained; NewsAPI was never in scope to begin
with but follows the identical pattern).

Mirrors the existing NotImplementedError convention in
src/misinformation/misinformation_classifier.py's MuRILClassifier/
TransformerClassifier/LLMComparisonClassifier stubs: the shape of the
integration is visible and explainable in a viva, but it does not
silently no-op or fake data -- fetch() raises FeedNotConfiguredError
naming the exact missing env var, and the caller (scheduler.py) records
that as feed status "not_configured", visibly distinct from "error".
"""
from app.config import settings
from app.external_feeds.base import ExternalEvent, ExternalFeedSource, FeedNotConfiguredError


class NewsAPIFeedSource(ExternalFeedSource):
    name = "NewsAPI"

    def fetch(self) -> list[ExternalEvent]:
        if not settings.news_api_key:
            raise FeedNotConfiguredError("NEWS_API_KEY is not set -- see .env.example")
        raise NotImplementedError("NewsAPI integration not written -- no key was available to test against")


class GoogleFactCheckFeedSource(ExternalFeedSource):
    name = "GoogleFactCheck"

    def fetch(self) -> list[ExternalEvent]:
        if not settings.google_fact_check_api_key:
            raise FeedNotConfiguredError("GOOGLE_FACT_CHECK_API_KEY is not set -- see .env.example")
        raise NotImplementedError("Google Fact Check Tools API integration not written -- no key was available to test against")


class RedditFeedSource(ExternalFeedSource):
    name = "Reddit"

    def fetch(self) -> list[ExternalEvent]:
        if not (settings.reddit_client_id and settings.reddit_client_secret):
            raise FeedNotConfiguredError("REDDIT_CLIENT_ID/REDDIT_CLIENT_SECRET are not set -- see .env.example")
        raise NotImplementedError("Reddit (PRAW) integration not written -- OAuth app was never approved (see STATUS.md)")


class TelegramFeedSource(ExternalFeedSource):
    name = "Telegram"

    def fetch(self) -> list[ExternalEvent]:
        if not (settings.telegram_api_id and settings.telegram_api_hash):
            raise FeedNotConfiguredError("TELEGRAM_API_ID/TELEGRAM_API_HASH are not set -- see .env.example")
        raise NotImplementedError("Telegram (Telethon) integration not written -- credentials were never obtained (see STATUS.md)")
