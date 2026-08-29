from app.scripts.seed_historical_claims import _fix_mojibake


def test_fixes_cp1252_mojibake_from_latin1_misdecode():
    broken = "Drones, radars, remote cameras \x97 Uttarakhand floods rescue effort is India\x92s most hi-tech yet"
    fixed = _fix_mojibake(broken)
    assert "\x97" not in fixed
    assert "\x92" not in fixed
    assert "—" in fixed  # em-dash
    assert "India’s" in fixed  # right single quote


def test_leaves_ordinary_text_unchanged():
    text = "Heavy rainfall has caused severe flooding in Whitefield, Bengaluru."
    assert _fix_mojibake(text) == text
