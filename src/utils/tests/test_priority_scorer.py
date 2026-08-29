from utils.priority_scorer import score_priority


def test_severe_specific_claim_is_high_priority():
    r = score_priority(
        "Whitefield flooding: 5 dead, NDRF conducts rescue operation",
        "Flood", "locality", "TRUE",
    )
    assert r.level == "HIGH"


def test_non_disaster_claim_is_low_priority():
    r = score_priority("Political storm erupts over minister's remarks", "None", "none", "FAKE")
    assert r.level == "LOW"


def test_unverified_verdict_adds_review_flag_reason():
    r = score_priority("Moderate quake felt across Delhi NCR", "Earthquake", "state", "UNVERIFIED")
    assert any("uncertain" in reason for reason in r.reasons)
