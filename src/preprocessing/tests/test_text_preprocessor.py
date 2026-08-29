import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from preprocessing.text_preprocessor import SocialMediaTextPreprocessor


def test_strips_urls_and_mentions_keeps_hashtag_word():
    pre = SocialMediaTextPreprocessor()
    out = pre.clean("Check https://x.co/abc now!! #FloodAlert @ndrf")
    assert "https://x.co/abc" not in out
    assert "@ndrf" not in out
    assert "FloodAlert" in out


def test_collapses_repeated_chars_without_mangling_double_letters():
    pre = SocialMediaTextPreprocessor()
    assert pre.clean("soooo bad") == "soo bad"
    # "flood" and "rescue" style genuine double letters must survive untouched
    assert "flood" in pre.clean("Heavy flood in the city")
    assert "rescue" in pre.clean("rescue operation underway")


def test_empty_and_whitespace_input_does_not_raise():
    pre = SocialMediaTextPreprocessor()
    assert pre.clean("") == ""
    assert pre.clean("   ") == ""
    assert pre.clean(None) == ""
