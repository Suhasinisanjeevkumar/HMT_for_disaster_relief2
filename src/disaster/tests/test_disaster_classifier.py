from disaster.disaster_classifier import KeywordDisasterClassifier


def test_flood_claim_classified_as_flood():
    clf = KeywordDisasterClassifier()
    r = clf.classify("Heavy rainfall has caused severe flooding in Whitefield, Bengaluru.")
    assert r.is_disaster_related is True
    assert r.primary_type == "Flood"


def test_non_disaster_text_not_related():
    clf = KeywordDisasterClassifier()
    r = clf.classify("Assembly election results to be declared tomorrow")
    assert r.is_disaster_related is False
    assert r.primary_type == "None"


def test_documented_political_storm_false_positive():
    """Known, documented limitation (see DISASTER_KEYWORDS comment in
    disaster_classifier.py): bare 'storm' matches non-weather usage too.
    This test asserts the CURRENT documented behavior so a future change
    to that tradeoff is a deliberate decision, not an accidental regression."""
    clf = KeywordDisasterClassifier()
    r = clf.classify("Political storm erupts over minister's remarks")
    assert r.is_disaster_related is True
    assert "Storm" in r.disaster_types
