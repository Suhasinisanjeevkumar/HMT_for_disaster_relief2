"""
In-memory per-source feed health tracker. Deliberately in-memory, not a DB
table -- this is operational status about the app's OWN external
connections, not user-facing claim/evidence data, and resets on restart by
design (a stale "last success" from a previous process isn't meaningful).

Three states, kept visually distinct wherever this is shown (API response,
About/Dashboard pages) -- collapsing them into one "is it working?" boolean
would hide exactly the information Module 1 / academic-honesty (spec
sections 4 and 29) cares about:
  "ok"             -- last fetch attempt succeeded
  "error"          -- last fetch attempt failed (network/parsing) -- transient
  "not_configured" -- this source needs credentials that were never
                       obtained (see stub_feeds.py / .env.example) -- permanent
                       until the user supplies them, not a bug
"""
import threading
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional


@dataclass
class FeedHealth:
    name: str
    status: str = "unknown"  # "ok" | "error" | "not_configured" | "unknown" (never fetched yet)
    last_attempt_at: Optional[datetime] = None
    last_success_at: Optional[datetime] = None
    last_error: Optional[str] = None
    last_event_count: int = 0


class FeedStatusRegistry:
    def __init__(self):
        self._lock = threading.Lock()
        self._health: dict[str, FeedHealth] = {}

    def record_success(self, name: str, event_count: int) -> None:
        with self._lock:
            now = datetime.now(timezone.utc)
            h = self._health.setdefault(name, FeedHealth(name=name))
            h.status = "ok"
            h.last_attempt_at = now
            h.last_success_at = now
            h.last_error = None
            h.last_event_count = event_count

    def record_error(self, name: str, error: str) -> None:
        with self._lock:
            h = self._health.setdefault(name, FeedHealth(name=name))
            h.status = "error"
            h.last_attempt_at = datetime.now(timezone.utc)
            h.last_error = error

    def record_not_configured(self, name: str, reason: str) -> None:
        with self._lock:
            h = self._health.setdefault(name, FeedHealth(name=name))
            h.status = "not_configured"
            h.last_attempt_at = datetime.now(timezone.utc)
            h.last_error = reason

    def all(self) -> list[FeedHealth]:
        with self._lock:
            return list(self._health.values())


registry = FeedStatusRegistry()
