from utils.reliability_scorer import score_reliability


def test_high_confidence_matched_corroborated_locality_is_high():
    r = score_reliability(
        misinfo_confidence=0.9, verification_matched=True, verification_similarity=0.8,
        verification_threshold=0.35, live_evidence_count=2, live_evidence_source_count=2,
        location_level="locality", evidence_type_matches=True,
    )
    assert r.band == "HIGH"


def test_nothing_at_all_is_low():
    r = score_reliability(
        misinfo_confidence=0.5, verification_matched=False, verification_similarity=0.0,
        verification_threshold=0.35, live_evidence_count=0, live_evidence_source_count=0,
        location_level=None, evidence_type_matches=None,
    )
    assert r.band == "LOW"


def test_evidence_with_wrong_disaster_type_withholds_coherence_bonus_and_explains_why():
    r = score_reliability(
        misinfo_confidence=0.7, verification_matched=False, verification_similarity=0.0,
        verification_threshold=0.35, live_evidence_count=1, live_evidence_source_count=1,
        location_level="city", evidence_type_matches=False,
    )
    assert r.breakdown["type_coherence"] == 0
    assert any("different disaster type" in reason for reason in r.reasons)
