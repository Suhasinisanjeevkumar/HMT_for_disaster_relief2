from location.location_extractor import GazetteerLocationExtractor


def test_bengaluru_bangalore_rename_alias_resolves():
    ext = GazetteerLocationExtractor()
    r = ext.extract("Heavy rain causes flooding in Bengaluru.")
    assert any(m.state == "Karnataka" for m in r.locations)


def test_bihar_state_vs_village_collision_resolves_to_state():
    """Documented tradeoff in gazetteer.py: state lookup runs before
    locality/city/district specifically so 'Bihar' resolves to the STATE,
    not the same-named village in Unnao district, UP."""
    ext = GazetteerLocationExtractor()
    r = ext.extract("Flood situation in Bihar remains critical")
    best = r.best
    assert best is not None
    assert best.match_level == "state"
    assert best.state == "Bihar"


def test_best_pick_is_deterministic_across_repeated_calls():
    """Regression for a real bug found during development: candidate
    generation used to use set(), whose iteration order is hash-randomized
    per-process -- the same input could non-deterministically resolve to
    a different 'best' location. Candidate generation is list-based now."""
    ext = GazetteerLocationExtractor()
    text = "Flooding in Whitefield and Marathahalli, Bengaluru."
    results = [ext.extract(text).best.matched_text for _ in range(20)]
    assert len(set(results)) == 1
