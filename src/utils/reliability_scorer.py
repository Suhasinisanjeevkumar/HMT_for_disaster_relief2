"""
Stage 6.5 -- Reliability scoring.

Distinct from priority_scorer.score_priority() on purpose: priority
answers "how much attention does this need" (independent of truth,
per that module's own docstring); reliability answers "how much
independent support exists for trusting this claim's verdict." Before
this module existed, ML confidence and stored/live evidence were three
separate numbers scattered across the pipeline result with nothing
combining them into one transparent, explainable score.

Rule-based and additive, exactly like priority_scorer.py, NOT a trained
score -- there is no reliability ground truth to train against, and
pretending otherwise would repeat the exact mistake STATUS.md already
documents for the UNVERIFIED band (an operational definition, not a
learned one).

Score components (max 100, each documented so it can be defended in a
viva):
  up to 35  ML model confidence: round(confidence * 35)
  up to 20  Stored-corpus verification (SourceVerifier): +15 flat if
            matched, +0-5 more scaled by how far the similarity exceeds
            SourceVerifier.MATCH_THRESHOLD
  up to 25  Live external evidence (USGS/ReliefWeb/GDACS, via
            backend/app/external_feeds/evidence_matcher.py): +15 if >=1
            topically+geographically+recency-relevant item was found,
            +10 more if >=2 INDEPENDENT sources corroborate
  up to 10  Location specificity: locality/city = 10, district = 5,
            state = 2, none = 0
  up to 10  Disaster-type/evidence coherence: +10 ONLY if evidence
            (stored OR live) exists and its disaster type matches the
            claim's primary type. If evidence exists but the type does
            NOT match, this is explicitly flagged in `reasons` as a
            caveat ("evidence found, but for a different disaster type")
            rather than silently scoring 0 with no explanation. If there
            is no evidence at all, coherence is also 0, with its own
            distinct "nothing to assess" reason -- not conflated with the
            type-mismatch case.

Bands: HIGH >= 70, MEDIUM 40-69, LOW < 40 -- a judgment call, stated as
one, at the same confidence level as priority_scorer.py's own thresholds.

NEVER conflate this score with "P(this claim is true)". It measures
independent support for the verdict, not the verdict's own confidence --
that's exactly why ML confidence is kept as its own, separate, capped
component in the breakdown rather than being the whole score.
"""
from dataclasses import dataclass, field
from typing import Optional

LOCATION_SPECIFICITY_POINTS = {"locality": 10, "city": 10, "district": 5, "state": 2}

HIGH_THRESHOLD = 70
MEDIUM_THRESHOLD = 40


@dataclass
class ReliabilityResult:
    score: int
    band: str  # HIGH | MEDIUM | LOW
    reasons: list = field(default_factory=list)
    breakdown: dict = field(default_factory=dict)


def score_reliability(
    misinfo_confidence: float,
    verification_matched: bool,
    verification_similarity: float,
    verification_threshold: float,
    live_evidence_count: int,
    live_evidence_source_count: int,
    location_level: Optional[str],
    evidence_type_matches: Optional[bool],
) -> ReliabilityResult:
    reasons = []
    breakdown = {}

    ml_component = round(misinfo_confidence * 35)
    breakdown["ml_confidence"] = ml_component
    reasons.append(f"ML classification confidence contributes {ml_component}/35")

    verification_component = 0
    if verification_matched:
        verification_component = 15
        span = max(1e-9, 1 - verification_threshold)
        bonus = round(min(5, max(0, (verification_similarity - verification_threshold) / span * 5)))
        verification_component += bonus
        reasons.append(f"matched a stored-corpus record ({verification_similarity:.0%} similarity) (+{verification_component}/20)")
    else:
        reasons.append("no stored-corpus match found (+0/20)")
    breakdown["stored_verification"] = verification_component

    live_component = 0
    if live_evidence_count >= 1:
        live_component += 15
        reasons.append(f"{live_evidence_count} relevant live evidence item(s) found (+15/25)")
        if live_evidence_source_count >= 2:
            live_component += 10
            reasons.append(f"corroborated by {live_evidence_source_count} independent live sources (+10/25)")
    else:
        reasons.append("no live external evidence found (+0/25)")
    breakdown["live_evidence"] = live_component

    location_component = LOCATION_SPECIFICITY_POINTS.get(location_level, 0)
    breakdown["location_specificity"] = location_component
    if location_component:
        reasons.append(f"location resolved at '{location_level}' level (+{location_component}/10)")
    else:
        reasons.append("no specific enough location resolved (+0/10)")

    coherence_component = 0
    if evidence_type_matches is True:
        coherence_component = 10
        reasons.append("evidence disaster type matches the claim's disaster type (+10/10)")
    elif evidence_type_matches is False:
        reasons.append(
            "evidence found, but for a different disaster type, so it does not corroborate "
            "this specific claim (+0/10)"
        )
    else:
        reasons.append("no evidence available to assess disaster-type coherence (+0/10)")
    breakdown["type_coherence"] = coherence_component

    score = min(100, ml_component + verification_component + live_component + location_component + coherence_component)
    band = "HIGH" if score >= HIGH_THRESHOLD else "MEDIUM" if score >= MEDIUM_THRESHOLD else "LOW"

    return ReliabilityResult(score=score, band=band, reasons=reasons, breakdown=breakdown)


if __name__ == "__main__":
    tests = [
        dict(misinfo_confidence=0.9, verification_matched=True, verification_similarity=0.8,
             verification_threshold=0.35, live_evidence_count=2, live_evidence_source_count=2,
             location_level="locality", evidence_type_matches=True),
        dict(misinfo_confidence=0.5, verification_matched=False, verification_similarity=0.0,
             verification_threshold=0.35, live_evidence_count=0, live_evidence_source_count=0,
             location_level=None, evidence_type_matches=None),
        dict(misinfo_confidence=0.7, verification_matched=False, verification_similarity=0.0,
             verification_threshold=0.35, live_evidence_count=1, live_evidence_source_count=1,
             location_level="city", evidence_type_matches=False),
    ]
    for t in tests:
        r = score_reliability(**t)
        print(f"\n{t}")
        print(f"  Reliability: {r.band} (score={r.score})  breakdown={r.breakdown}")
        for reason in r.reasons:
            print(f"    - {reason}")
