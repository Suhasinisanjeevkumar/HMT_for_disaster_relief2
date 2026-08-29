"""
Gazetteer -- loads a real Indian locality dataset (India Post office
directory: ~39,700 post offices, each with locality/city/district/state)
and provides lookup + fuzzy-match helpers.

Data source: kishorek/India-Codes (GitHub), itself derived from India Post's
official pincode directory. Saved locally at data/external/pincodes_kishorek.csv
so this module has no network dependency at runtime.

Known limitation (say this in your viva if asked): this is a real government-
sourced dataset, but it's not perfect or fully current -- e.g. "Whitefield"
(the Bengaluru locality) isn't in the data under that exact spelling; it's
filed as "White Field" (two words). Exact lookup misses that; fuzzy lookup
catches it. That gap is normal for any gazetteer and is exactly why fuzzy
matching is part of this module rather than an afterthought.
"""
import csv
import difflib
import os
from dataclasses import dataclass
from typing import Dict, List, Optional

DATA_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "data", "external", "pincodes_kishorek.csv"
)

# This dataset (like many Indian gazetteers) predates several official renames
# and doesn't consistently use the current names. Plain fuzzy string matching
# does NOT reliably catch these -- e.g. "Bengaluru" is character-closer to an
# unrelated small locality called "Benbalur" (ratio 0.82) than to "Bangalore"
# (ratio 0.67), so fuzzy matching alone actively picks the WRONG place. This
# alias table is the real fix: known renames are mapped explicitly, checked
# before any fuzzy matching happens. If you extend the gazetteer later, check
# new place names against this list -- it's the same failure mode.
RENAME_ALIASES = {
    "bengaluru": "bangalore",       # city, renamed 2014, dataset predates it
    "odisha": "orissa",             # state, renamed 2011
    "uttarakhand": "uttaranchal",   # state, renamed 2007
    "puducherry": "pondicherry",    # state/UT
    "gurugram": "gurgaon",          # city, renamed 2016
    "prayagraj": "allahabad",       # city, renamed 2018
    # informal short forms news headlines commonly use for full state names --
    # same collision problem as above: "Arunachal" alone exactly matches an
    # unrelated locality in Assam, so without this alias it silently resolved
    # to the wrong state entirely.
    "arunachal": "arunachal pradesh",
    "andhra": "andhra pradesh",
    "himachal": "himachal pradesh",
    "madhya": "madhya pradesh",
}


def _normalize(name: str) -> str:
    key = " ".join(str(name).strip().lower().split())
    return RENAME_ALIASES.get(key, key)


@dataclass
class GazetteerEntry:
    locality: str
    city: str
    district: str
    state: str
    country: str = "India"


class Gazetteer:
    def __init__(self, csv_path: str = DATA_PATH):
        self.entries: List[GazetteerEntry] = []
        self._locality_index: Dict[str, GazetteerEntry] = {}
        # city/district/state indexes deliberately store ONLY the fields that
        # granularity actually determines -- a match on "Assam" (a state)
        # must NOT claim a specific city/district that the input never
        # mentioned. Mixing granularities was an earlier bug in this file.
        self._city_index: Dict[str, Dict[str, str]] = {}        # -> {city, district, state}
        self._district_index: Dict[str, Dict[str, str]] = {}    # -> {district, state}
        self._state_index: Dict[str, str] = {}                  # -> canonical state name

        # first-letter buckets, built once, so fuzzy matching doesn't have to
        # scan all ~39,700 entries for every candidate -- only the ones that
        # plausibly could match (same first letter after normalization).
        self._locality_buckets: Dict[str, List[str]] = {}
        self._city_buckets: Dict[str, List[str]] = {}

        self._load(csv_path)

    def _load(self, csv_path: str):
        with open(csv_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                state = row.get("State")
                if not state or not state.strip():
                    continue
                locality = row.get("PostOfficeName", "").strip()
                city = (row.get("City") or "").strip() or locality
                district = (row.get("DistrictsName") or "").strip()
                state = state.strip()
                entry = GazetteerEntry(locality=locality, city=city, district=district, state=state)
                self.entries.append(entry)

                loc_key = _normalize(locality)
                city_key = _normalize(city)
                dist_key = _normalize(district)
                state_key = _normalize(state)

                self._locality_index.setdefault(loc_key, entry)
                self._city_index.setdefault(city_key, {"city": city, "district": district, "state": state})
                if dist_key:
                    self._district_index.setdefault(dist_key, {"district": district, "state": state})
                self._state_index.setdefault(state_key, state)

                self._locality_buckets.setdefault(loc_key[:1], []).append(loc_key)
                self._city_buckets.setdefault(city_key[:1], []).append(city_key)

    # ---- exact lookups ----
    # Note the deliberately different return shapes: a locality match is backed
    # by one real row so it can return the full hierarchy; state/district
    # matches only return what that granularity actually determines.
    def lookup_locality(self, name: str) -> Optional[GazetteerEntry]:
        return self._locality_index.get(_normalize(name))

    def lookup_city(self, name: str) -> Optional[dict]:
        return self._city_index.get(_normalize(name))

    def lookup_district(self, name: str) -> Optional[dict]:
        return self._district_index.get(_normalize(name))

    def lookup_state(self, name: str) -> Optional[str]:
        return self._state_index.get(_normalize(name))

    # ---- fuzzy lookups (bucketed by first letter for speed) ----
    # cutoff=0.88 rather than a looser value deliberately: at 0.82 the matcher
    # was picking "Benbalur" over "Bangalore" for the input "Bengaluru" (see
    # module docstring) -- character-level similarity isn't semantic
    # similarity, so the threshold has to be conservative. Known renames are
    # handled by RENAME_ALIASES above, not by loosening this cutoff.
    def fuzzy_locality(self, name: str, cutoff: float = 0.88):
        best, score = self._fuzzy(name, self._locality_buckets, cutoff)
        return (self._locality_index[best] if best else None), score

    def fuzzy_city(self, name: str, cutoff: float = 0.88):
        best, score = self._fuzzy(name, self._city_buckets, cutoff)
        return (self._city_index[best] if best else None), score

    def _fuzzy(self, name: str, buckets: Dict[str, List[str]], cutoff: float):
        key = _normalize(name)
        if not key:
            return None, 0.0
        pool = buckets.get(key[:1], [])
        if not pool:
            return None, 0.0
        matches = difflib.get_close_matches(key, pool, n=1, cutoff=cutoff)
        if not matches:
            return None, 0.0
        best = matches[0]
        score = difflib.SequenceMatcher(None, key, best).ratio()
        return best, score


if __name__ == "__main__":
    gz = Gazetteer()
    print(f"Loaded {len(gz.entries)} gazetteer entries "
          f"({len(gz._state_index)} states, {len(gz._city_index)} distinct cities, "
          f"{len(gz._locality_index)} distinct localities)")

    tests = ["Whitefield", "whitefield", "Bengaluru", "Bangalore", "Odisha", "Uttarakhand",
             "Assam", "Kerala", "Gurugram", "Nonexistentplace123"]
    for t in tests:
        loc = gz.lookup_locality(t)
        city = gz.lookup_city(t)
        state = gz.lookup_state(t)
        if loc:
            print(f"  EXACT locality '{t}' -> {loc}")
        elif city:
            print(f"  EXACT city     '{t}' -> {city}")
        elif state:
            print(f"  EXACT state    '{t}' -> {state}")
        else:
            entry, score = gz.fuzzy_locality(t)
            if entry:
                print(f"  FUZZY locality '{t}' -> {entry}  (score={score:.2f})")
            else:
                print(f"  NONE           '{t}' -> no match")
