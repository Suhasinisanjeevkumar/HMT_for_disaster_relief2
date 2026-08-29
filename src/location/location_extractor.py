"""
Location extraction -- finds place-name candidates in claim text and
resolves them against the Gazetteer, at whatever granularity actually
matches (locality / city / district / state).

Design note: same interface pattern as Stage 2's DisasterClassifier.
LocationExtractor is an abstract interface; GazetteerLocationExtractor is
today's implementation (regex candidate generation + gazetteer lookup, no
external NER model). When you're ready to add spaCy or an Indic NER model,
write a class with the same `.extract(text)` method -- nothing else in the
project changes. This is intentionally NOT using spaCy yet: it adds a
model-download dependency for a marginal gain over regex on short,
place-name-in-headline text, which is most of what's in this dataset.
"""
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional

from .gazetteer import Gazetteer

# Capitalized-word-sequence candidate pattern: catches "Whitefield",
# "New Delhi", "Bengaluru, Karnataka" as separate candidates (comma/period
# breaks a phrase; this deliberately does NOT try to be a full grammar).
CANDIDATE_PATTERN = re.compile(r"\b[A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+){0,2}\b")

# Common capitalized words that are NOT places but pass the regex above --
# without this, every capitalized word becomes a false location candidate.
# This list is necessarily incomplete; it's a practical filter, not a solved
# problem. The second set specifically targets a real failure mode found
# while testing this module: ordinary English words get capitalized purely
# because they follow a colon or full stop in headline style ("landslide:
# More bodies found") -- "More" then exact-matched a real locality in Bihar,
# outranking the correct match elsewhere in the same sentence. These are
# common clause-initial function/modal words, not an exhaustive dictionary.
NON_LOCATION_STOP = {
    "the", "a", "an", "fact", "check", "claim", "video", "photo", "image",
    "old", "viral", "shared", "true", "false", "fake", "news", "india",
    "government", "minister", "police", "covid", "pm", "bjp", "congress",
    "more", "most", "less", "least", "many", "some", "few", "all", "each",
    "every", "any", "no", "none", "not", "also", "even", "just", "only",
    "still", "yet", "will", "shall", "may", "might", "can", "could",
    "should", "would", "must", "about", "after", "amid", "among", "before",
    "during", "following", "over", "under", "new", "amid", "as", "so",
}


@dataclass
class LocationMatch:
    matched_text: str
    match_level: str          # "locality" | "city" | "district" | "state" | "none"
    match_type: str           # "exact" | "fuzzy"
    confidence: float
    locality: Optional[str] = None
    city: Optional[str] = None
    district: Optional[str] = None
    state: Optional[str] = None
    country: str = "India"
    text_order: int = 0  # position candidate first appeared in the input text, used as a tiebreak
    pincode: Optional[str] = None  # only ever set for exact locality matches -- see GazetteerEntry.pincode


@dataclass
class LocationExtractionResult:
    locations: List[LocationMatch] = field(default_factory=list)

    @property
    def best(self) -> Optional[LocationMatch]:
        """Most specific match found, if any (locality > city > district > state).
        Ties within the same level: prefer a locality distinct from its city
        (more informative), then whichever was mentioned FIRST in the text --
        news-style writing conventionally leads with the primary/dateline
        location, so this is a real heuristic, not an arbitrary pick."""
        order = {"locality": 0, "city": 1, "district": 2, "state": 3}
        if not self.locations:
            return None

        def sort_key(m: LocationMatch):
            redundant = 1 if (m.locality and m.locality == m.city) else 0
            return (order.get(m.match_level, 9), redundant, m.text_order)

        return sorted(self.locations, key=sort_key)[0]


class LocationExtractor(ABC):
    @abstractmethod
    def extract(self, text: str) -> LocationExtractionResult:
        raise NotImplementedError


class GazetteerLocationExtractor(LocationExtractor):
    def __init__(self, gazetteer: Optional[Gazetteer] = None):
        self.gz = gazetteer or Gazetteer()

    def _candidates(self, text: str) -> List[str]:
        """Returns candidates in a deterministic order (first appearance in
        text). Earlier versions used a set() here, which has process-level
        hash-randomized iteration order in Python -- same input could produce
        a different "best" match on different runs/machines. Confirmed this
        happening in testing (a two-location claim non-deterministically
        picked either location as "best"), so order must be stable now."""
        found = CANDIDATE_PATTERN.findall(text)
        ordered: List[str] = []
        seen_lower = set()
        for c in found:
            words = [c] + c.split()
            for w in words:
                wl = w.lower()
                if wl in NON_LOCATION_STOP or len(w) <= 2 or wl in seen_lower:
                    continue
                seen_lower.add(wl)
                ordered.append(w)
        return ordered

    def _resolve_one(self, candidate: str) -> Optional[LocationMatch]:
        # State check runs FIRST, ahead of locality/city/district, even
        # though a state match is the least "specific" result. Reason: a
        # handful of state names exactly collide with an unrelated village's
        # name elsewhere in the gazetteer -- "Bihar" (the state) is also the
        # name of a village in Unnao district, UP; same for "Punjab". Without
        # this, "flood in Bihar" was resolving to a random UP village instead
        # of the state of Bihar, which is a much worse error than losing
        # locality-level precision on the rare genuine village-named-Bihar
        # case. Checked empirically: only 4 such collisions exist in this
        # gazetteer (see src/location/gazetteer.py history) -- an acceptable,
        # documented tradeoff rather than a silent one.
        state = self.gz.lookup_state(candidate)
        if state:
            return LocationMatch(candidate, "state", "exact", 1.0,
                                  None, None, None, state)

        loc = self.gz.lookup_locality(candidate)
        if loc:
            return LocationMatch(candidate, "locality", "exact", 1.0,
                                  loc.locality, loc.city, loc.district, loc.state,
                                  pincode=(loc.pincode or None))

        city = self.gz.lookup_city(candidate)
        if city:
            return LocationMatch(candidate, "city", "exact", 1.0,
                                  None, city["city"], city["district"], city["state"])

        district = self.gz.lookup_district(candidate)
        if district:
            return LocationMatch(candidate, "district", "exact", 1.0,
                                  None, None, district["district"], district["state"])

        # fuzzy fallback, locality first (most useful if it hits), then city
        loc, score = self.gz.fuzzy_locality(candidate)
        if loc:
            return LocationMatch(candidate, "locality", "fuzzy", score,
                                  loc.locality, loc.city, loc.district, loc.state)
        city, score = self.gz.fuzzy_city(candidate)
        if city:
            return LocationMatch(candidate, "city", "fuzzy", score,
                                  None, city["city"], city["district"], city["state"])

        return None

    def extract(self, text: str) -> LocationExtractionResult:
        result = LocationExtractionResult()
        seen_keys = set()
        for order, candidate in enumerate(self._candidates(text)):
            match = self._resolve_one(candidate)
            if match:
                key = (match.locality, match.city, match.district, match.state)
                if key not in seen_keys:
                    seen_keys.add(key)
                    match.text_order = order  # deterministic tiebreak, see LocationMatch.best
                    result.locations.append(match)
        return result


if __name__ == "__main__":
    extractor = GazetteerLocationExtractor()
    samples = [
        "Heavy rain causes flooding in Whitefield, Bengaluru.",
        "Cyclone warning issued for coastal Odisha districts",
        "NDRF teams deployed after flash floods in Uttarakhand",
        "5 more die as flood situation in Assam remains critical",
        "Political storm erupts over minister's remarks",  # no real location expected
    ]
    for s in samples:
        res = extractor.extract(s)
        print(f"\n{s}")
        if not res.locations:
            print("  No location resolved.")
        for m in res.locations:
            print(f"  [{m.match_level}/{m.match_type} conf={m.confidence:.2f}] "
                  f"'{m.matched_text}' -> locality={m.locality}, city={m.city}, "
                  f"district={m.district}, state={m.state}")
        if res.best:
            b = res.best
            print(f"  BEST: {b.locality or b.city or b.district or b.state} "
                  f"({b.match_level}, {b.state})")
