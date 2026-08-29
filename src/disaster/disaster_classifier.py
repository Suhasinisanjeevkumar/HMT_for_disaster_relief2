"""
Stage 2 — Disaster type classification.

Design note (why it's structured this way):
Your Stage 1 filter only answers "is this disaster-related?" (True/False).
This module answers "which disaster type(s)?" (Flood, Cyclone, Earthquake, ...).

It's written as an interface (`DisasterClassifier`) with one implementation
(`KeywordDisasterClassifier`) so that later you can write a second
implementation -- e.g. `MLDisasterClassifier` -- that plugs into the exact
same `.classify(text)` call. Nothing downstream needs to change when you
swap it; that's the whole point of the interface.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List
import re


# One regex-friendly keyword/phrase list per disaster type. Multi-word phrases
# are safer than bare words -- e.g. bare "storm" also matches "political storm",
# so where a category is prone to that, phrases are preferred over single words.
DISASTER_KEYWORDS: Dict[str, List[str]] = {
    "Flood": [
        r"flood\w*", r"flash flood", r"water\s?logg\w*", r"deluge", r"inundat\w*",
    ],
    "Cyclone": [
        r"cyclon\w*", r"hurricane", r"typhoon", r"storm surge",
    ],
    "Earthquake": [
        r"earthquake", r"\bquakes?\b", r"tremors?", r"seismic",
    ],
    "Landslide": [
        r"landslide", r"mudslide", r"rockslide",
    ],
    "Heavy Rain": [
        r"heavy rain\w*", r"torrential rain\w*", r"incessant rain\w*", r"heavy rainfall",
    ],
    "Cloudburst": [
        r"cloudburst",
    ],
    "Drought": [
        r"drought", r"water scarcity", r"dry spell",
    ],
    "Wildfire": [
        r"wildfire", r"forest fire", r"bushfire",
    ],
    "Tsunami": [
        r"tsunami",
    ],
    "Avalanche": [
        r"avalanche",
    ],
    "Storm": [
        r"thunderstorm", r"squall", r"\bstorm\b",  # bare "storm" included last / lowest priority - see KNOWN LIMITATION below
    ],
    "Rescue/Evacuation": [
        r"rescue operation\w*", r"rescue team\w*", r"search and rescue",
        r"evacuat\w*", r"relief camp\w*", r"relief operation\w*", r"\bndrf\b", r"\bsdrf\b",
    ],
}

# Generic disaster-management terms that don't name a specific type but do
# indicate disaster relevance -- feeds the "Other" bucket.
OTHER_DISASTER_TERMS = [
    r"disaster management", r"\bndma\b", r"\bsdma\b", r"natural disaster",
    r"red alert", r"orange alert", r"death toll ris\w*", r"imd warning",
]

# KNOWN LIMITATION (be ready to say this in your viva):
# Bare words like "storm" and "rescue" are ambiguous out of context
# ("political storm", "hostage rescue"). They're kept because dropping them
# loses real disaster claims, but expect some false positives in the
# Storm and Rescue/Evacuation categories specifically. A future ML classifier
# (Stage 4 style, on this same interface) is the real fix for this -- rules
# can't easily tell "storm" (weather) from "storm" (metaphor).


@dataclass
class DisasterClassificationResult:
    is_disaster_related: bool
    disaster_types: List[str]                  # every category that matched, e.g. ["Flood", "Rescue/Evacuation"]
    primary_type: str                           # the single best-guess type (most keyword hits), or "None"
    matched_keywords: Dict[str, List[str]] = field(default_factory=dict)  # category -> matched terms, for explainability


class DisasterClassifier(ABC):
    """Interface. Swap KeywordDisasterClassifier for an ML version later
    by writing a class that implements this same method."""

    @abstractmethod
    def classify(self, text: str) -> DisasterClassificationResult:
        raise NotImplementedError


class KeywordDisasterClassifier(DisasterClassifier):
    def __init__(self):
        self._compiled = {
            cat: re.compile("|".join(patterns), re.IGNORECASE)
            for cat, patterns in DISASTER_KEYWORDS.items()
        }
        self._other = re.compile("|".join(OTHER_DISASTER_TERMS), re.IGNORECASE)

    def classify(self, text: str) -> DisasterClassificationResult:
        text = text or ""
        matched: Dict[str, List[str]] = {}

        for cat, pattern in self._compiled.items():
            hits = pattern.findall(text)
            if hits:
                matched[cat] = sorted(set(h.lower() for h in hits))

        if not matched:
            other_hits = self._other.findall(text)
            if other_hits:
                matched["Other"] = sorted(set(h.lower() for h in other_hits))

        types = list(matched.keys())
        primary = max(matched, key=lambda k: len(matched[k])) if matched else "None"

        return DisasterClassificationResult(
            is_disaster_related=bool(types),
            disaster_types=types,
            primary_type=primary,
            matched_keywords=matched,
        )


if __name__ == "__main__":
    # quick manual smoke test -- run this file directly to sanity-check it
    clf = KeywordDisasterClassifier()
    samples = [
        "Heavy rainfall has caused severe flooding in Whitefield, Bengaluru.",
        "NDRF teams conduct rescue operation after cyclone Fani hits Odisha coast",
        "5.2 magnitude earthquake tremor felt across Delhi NCR",
        "Political storm erupts over minister's remarks",  # should show the known false-positive
        "Assembly election results to be declared tomorrow",  # not disaster-related at all
    ]
    for s in samples:
        r = clf.classify(s)
        print(f"\n{s}")
        print(f"  is_disaster_related = {r.is_disaster_related}")
        print(f"  disaster_types      = {r.disaster_types}")
        print(f"  primary_type        = {r.primary_type}")
        print(f"  matched_keywords    = {r.matched_keywords}")
