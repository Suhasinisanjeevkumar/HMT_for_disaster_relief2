from misinformation.misinformation_classifier import (
    TfidfLogRegClassifier,
    apply_verdict,
    UNVERIFIED_CONFIDENCE_THRESHOLD,
)


def test_predict_label_is_one_of_the_three_valid_verdicts():
    clf = TfidfLogRegClassifier()
    r = clf.predict("Heavy rain causes flooding in Whitefield, Bengaluru")
    assert r.label in ("TRUE", "FAKE", "UNVERIFIED")
    assert 0.0 <= r.confidence <= 1.0


def test_apply_verdict_boundary_at_threshold():
    just_above = UNVERIFIED_CONFIDENCE_THRESHOLD + 0.01
    just_below = UNVERIFIED_CONFIDENCE_THRESHOLD - 0.01

    label, conf = apply_verdict(just_above)  # P(true) high and confident
    assert label == "TRUE"

    label, conf = apply_verdict(1 - just_below)  # P(true) low -> confidence in FAKE is just_below -> UNVERIFIED
    assert label == "UNVERIFIED"


def test_top_terms_populated_for_vocabulary_containing_text():
    clf = TfidfLogRegClassifier()
    r = clf.predict("Old video of 2019 Kerala floods being shared as visuals from the current Assam flooding")
    assert len(r.top_terms) > 0
