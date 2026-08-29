"""
Stage 7 -- Priority scoring.

Rule-based and additive on purpose (per your spec: understandable, easy to
defend in a viva). Note this scores how much a claim NEEDS ATTENTION, not
"is this a real emergency" -- a highly specific, severe-sounding FAKE claim
still needs urgent attention (to debunk it before it spreads), which matches
your own spec's dashboard example: a FAKE flood claim with a specific
locality was still scored Priority: HIGH. So priority is independent of the
TRUE/FAKE/UNVERIFIED label; it's a measure of "how loud and specific is
this claim," not "how sure are we it's real."

Score components (each documented so you can defend the numbers):
  +3  disaster type severity weight (Earthquake/Tsunami/Cyclone = 3,
      Flood/Landslide/Cloudburst = 2, others = 1, "Other"/none = 0)
  +2  location resolved at locality level (most specific / actionable)
  +1  location resolved at city level
  +2  casualty/death-toll language present in the claim text
  +1  rescue/evacuation language present
  +1  infrastructure-damage language present
  +1  model verdict is UNVERIFIED (uncertain + specific claims need human
      review most -- this is the one place label DOES factor in, and only
      for the uncertain case)

Total score -> HIGH (>=5), MEDIUM (2-4), LOW (0-1). Thresholds are a
judgment call, not derived from data -- say so if asked in your viva.
"""
import re
from dataclasses import dataclass
from typing import Optional

TYPE_SEVERITY = {
    "Earthquake": 3, "Tsunami": 3, "Cyclone": 3,
    "Flood": 2, "Landslide": 2, "Cloudburst": 2, "Wildfire": 2, "Avalanche": 2,
    "Heavy Rain": 1, "Storm": 1, "Drought": 1, "Rescue/Evacuation": 2,
    "Other": 0, "None": 0, "Not disaster-related": 0,
}

CASUALTY_RE = re.compile(r"\b(died|dead|death toll|killed|casualt\w*|bodies found)\b", re.IGNORECASE)
RESCUE_RE = re.compile(r"\b(rescue\w*|evacuat\w*|ndrf|sdrf)\b", re.IGNORECASE)
INFRA_RE = re.compile(r"\b(bridge collapse|building collapse|road damaged|power outage|infrastructure damage)\b", re.IGNORECASE)


@dataclass
class PriorityResult:
    level: str          # "HIGH" | "MEDIUM" | "LOW"
    score: int
    reasons: list


def score_priority(text: str, disaster_type: str, location_level: Optional[str], verdict_label: str) -> PriorityResult:
    score = 0
    reasons = []

    type_score = TYPE_SEVERITY.get(disaster_type, 1)
    if type_score:
        score += type_score
        reasons.append(f"disaster type '{disaster_type}' (+{type_score})")

    if location_level == "locality":
        score += 2
        reasons.append("location specific to locality level (+2)")
    elif location_level == "city":
        score += 1
        reasons.append("location specific to city level (+1)")

    if CASUALTY_RE.search(text):
        score += 2
        reasons.append("casualty/death-toll language present (+2)")
    if RESCUE_RE.search(text):
        score += 1
        reasons.append("rescue/evacuation language present (+1)")
    if INFRA_RE.search(text):
        score += 1
        reasons.append("infrastructure damage language present (+1)")
    if verdict_label == "UNVERIFIED":
        score += 1
        reasons.append("model is uncertain -- flagged for human review (+1)")

    level = "HIGH" if score >= 5 else "MEDIUM" if score >= 2 else "LOW"
    return PriorityResult(level=level, score=score, reasons=reasons)


if __name__ == "__main__":
    tests = [
        ("Whitefield flooding: 5 dead, NDRF conducts rescue operation", "Flood", "locality", "TRUE"),
        ("Political storm erupts over minister's remarks", "None", "none", "FAKE"),
        ("Moderate quake felt across Delhi NCR", "Earthquake", "state", "UNVERIFIED"),
    ]
    for text, dtype, loc_level, verdict in tests:
        r = score_priority(text, dtype, loc_level, verdict)
        print(f"\n{text}")
        print(f"  Priority: {r.level} (score={r.score})")
        for reason in r.reasons:
            print(f"    - {reason}")
