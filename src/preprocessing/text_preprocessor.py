"""
Text preprocessing -- modular, swappable, and DELIBERATELY NOT wired into
the shipped misinformation model's inference path.

READ THIS BEFORE CHANGING WHERE THIS IS USED:
src/build_baseline.py fit TfidfVectorizer directly on raw, unmodified
IFND `Statement` text -- no URL-stripping, lowercasing-beyond-TF-IDF's-own-
default-tokenizer, or repeated-character collapsing happened at training
time. That means TfidfLogRegClassifier.predict() (misinformation/
misinformation_classifier.py) and SourceVerifier.verify() (verification/
source_verifier.py) both expect to see text shaped like that.

If a new cleaning step were inserted ahead of `self.vec.transform([text])`
at INFERENCE time only, the token distribution the model actually sees
would silently diverge from the distribution it was fit on. Nothing would
error -- the model would just quietly get worse, in a way that's easy to
miss and hard to diagnose later. So: this module is used ONLY to clean
text arriving from noisy external sources (RSS/API feeds, see
backend/app/external_feeds/) before that text is handed to the UNTRAINED,
regex-based KeywordDisasterClassifier and GazetteerLocationExtractor --
neither of which was "trained" on anything, so there is no train/inference
skew risk there. It is never called ahead of the misinformation classifier
or the verifier. See ARCHITECTURE.md for the same warning restated for
anyone who didn't read this docstring first.

If you do want preprocessing in front of the trained model someday, it
must be added to build_baseline.py's TRAINING text too, and
compare_baselines.py / MODEL_EVALUATION.md re-run from scratch.
"""
import html
import re
from abc import ABC, abstractmethod

URL_RE = re.compile(r"https?://\S+|www\.\S+")
MENTION_RE = re.compile(r"@\w+")
HASHTAG_RE = re.compile(r"#(\w+)")  # keeps the word, drops the '#'
REPEATED_CHAR_RE = re.compile(r"(.)\1{2,}")  # 3+ of the same char in a row
WHITESPACE_RE = re.compile(r"\s+")


class TextPreprocessor(ABC):
    @abstractmethod
    def clean(self, text: str) -> str:
        raise NotImplementedError


class SocialMediaTextPreprocessor(TextPreprocessor):
    """Cleans noisy social-media/RSS-derived text: strips URLs and
    @mentions, keeps hashtag words (drops just the '#'), unescapes HTML
    entities (RSS feeds are frequently HTML-escaped), collapses runs of
    3+ repeated characters down to 2 ("sooooo" -> "soo" -- 2, not 1, so
    genuine English double letters like "flood" or "rescue" are never
    touched), and collapses whitespace."""

    def clean(self, text: str) -> str:
        if not text:
            return ""
        text = html.unescape(text)
        text = URL_RE.sub("", text)
        text = MENTION_RE.sub("", text)
        text = HASHTAG_RE.sub(r"\1", text)
        text = REPEATED_CHAR_RE.sub(r"\1\1", text)
        text = WHITESPACE_RE.sub(" ", text).strip()
        return text


if __name__ == "__main__":
    pre = SocialMediaTextPreprocessor()
    samples = [
        "Check https://x.co/abc now!! #FloodAlert @ndrf",
        "soooo bad!!!! floooood everywhere",
        "   ",
        "&amp; water levels rising fast",
    ]
    for s in samples:
        print(f"{s!r} -> {pre.clean(s)!r}")
