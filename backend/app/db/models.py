"""
ORM models for the HMT backend.

Migration approach: Base.metadata.create_all(engine) on startup, no
Alembic. This is a single-developer dev-SQLite capstone project -- the
whole DB can be deleted and recreated at any point during development, so
Alembic's real value (safe, reversible, production migration history)
doesn't apply yet. The one real cost, stated plainly: a schema change
during development means deleting the dev .db file and reseeding. See
ARCHITECTURE.md for the full reasoning (same "don't build what you don't
need yet" philosophy as the NotImplementedError stubs in
src/misinformation/misinformation_classifier.py).

Claim.classification (the ML verdict) and the Evidence table are kept as
separate, never-merged concepts throughout this schema -- the ML model
does not "verify" anything; Evidence rows are the independently-sourced
support (or lack of it) for a claim. See src/verification/source_verifier.py
and backend/app/external_feeds/ for where each Evidence row comes from.
"""
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Claim(Base):
    __tablename__ = "claims"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    source: Mapped[str] = mapped_column(String(64), default="manual")
    source_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    submitted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    disaster_type: Mapped[str] = mapped_column(String(64), default="None")
    all_disaster_types: Mapped[list] = mapped_column(JSON, default=list)

    # The ML verdict -- see src/misinformation/misinformation_classifier.py.
    # This is a model prediction, not a fact-check result. Evidence rows
    # (below) are the separate, independently-sourced support layer.
    classification: Mapped[str] = mapped_column(String(16), default="UNVERIFIED")  # TRUE | FAKE | UNVERIFIED
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    top_terms: Mapped[list] = mapped_column(JSON, default=list)  # explainability, see misinformation_classifier.py

    reliability_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    reliability_band: Mapped[str | None] = mapped_column(String(16), nullable=True)  # HIGH | MEDIUM | LOW
    reliability_reasons: Mapped[list] = mapped_column(JSON, default=list)

    priority: Mapped[str] = mapped_column(String(16), default="LOW")  # HIGH | MEDIUM | LOW
    priority_score: Mapped[int] = mapped_column(Integer, default=0)
    priority_reasons: Mapped[list] = mapped_column(JSON, default=list)

    # "matched" / "not_matched" against the stored IFND corpus -- see
    # SourceVerifier. Distinct from live-feed Evidence, which is recorded
    # as its own Evidence rows rather than a single status string.
    verification_status: Mapped[str] = mapped_column(String(32), default="not_matched")

    reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    # True only for rows imported by seed_historical_claims.py from the
    # precomputed IFND dataset -- never for a live manual/API submission.
    # Always surfaced distinctly in the UI so historical demo data is never
    # mistaken for a real report.
    is_historical_seed: Mapped[bool] = mapped_column(Boolean, default=False)

    locations: Mapped[list["Location"]] = relationship(
        back_populates="claim", cascade="all, delete-orphan"
    )
    evidence: Mapped[list["Evidence"]] = relationship(
        back_populates="claim", cascade="all, delete-orphan"
    )
    alerts: Mapped[list["Alert"]] = relationship(
        back_populates="claim", cascade="all, delete-orphan"
    )


class Location(Base):
    __tablename__ = "locations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    claim_id: Mapped[int] = mapped_column(ForeignKey("claims.id"), nullable=False)

    matched_text: Mapped[str] = mapped_column(String(256))
    match_level: Mapped[str] = mapped_column(String(16))  # locality | city | district | state | none
    match_type: Mapped[str] = mapped_column(String(16))  # exact | fuzzy

    locality: Mapped[str | None] = mapped_column(String(256), nullable=True)
    city: Mapped[str | None] = mapped_column(String(256), nullable=True)
    district: Mapped[str | None] = mapped_column(String(256), nullable=True)
    state: Mapped[str | None] = mapped_column(String(128), nullable=True)
    pin_code: Mapped[str | None] = mapped_column(String(16), nullable=True)

    # Offline centroid lookup only -- see src/location/geocode_lookup.py.
    # No live geocoding call is ever made in the request path.
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    coordinate_precision: Mapped[str | None] = mapped_column(String(16), nullable=True)  # city | state | none

    # Mirrors LocationExtractionResult.best -- the location analyze_claim()
    # picked as the single most-specific/first-mentioned match.
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False)

    claim: Mapped["Claim"] = relationship(back_populates="locations")


class Evidence(Base):
    __tablename__ = "evidence"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    claim_id: Mapped[int] = mapped_column(ForeignKey("claims.id"), nullable=False)

    # e.g. "IFND_corpus" (SourceVerifier), "USGS", "ReliefWeb", "GDACS".
    source: Mapped[str] = mapped_column(String(64))
    url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    evidence_type: Mapped[str] = mapped_column(String(64))  # e.g. "corpus_similarity", "live_feed_match"
    description: Mapped[str] = mapped_column(Text)
    event_timestamp: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    matched_confidence: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    claim: Mapped["Claim"] = relationship(back_populates="evidence")


# Rendered verbatim wherever an alert is shown, so the "no real integration"
# caveat can never drift out of sync between the API and the UI -- see
# backend/app/services/alerts_service.py, which is the only place besides
# this constant's definition that ever needs to know this wording.
ALERT_SCOPE_NOTE = (
    "Flagged for relief-organization consideration. "
    "No emergency services have been contacted by this system."
)


class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    claim_id: Mapped[int] = mapped_column(ForeignKey("claims.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    level: Mapped[str] = mapped_column(String(16), default="HIGH")
    reason_text: Mapped[str] = mapped_column(Text)
    acknowledged: Mapped[bool] = mapped_column(Boolean, default=False)

    claim: Mapped["Claim"] = relationship(back_populates="alerts")
