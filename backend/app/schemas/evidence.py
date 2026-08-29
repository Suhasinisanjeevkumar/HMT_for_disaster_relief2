from datetime import datetime

from pydantic import BaseModel, ConfigDict

# Rendered next to every Evidence row in the UI so it's never confused with
# the ML verdict (Claim.classification) -- see app/db/models.py's module
# docstring and spec section "Evidence-Based Verification".
EVIDENCE_DISCLOSURE = (
    "Evidence rows are independently-sourced support (or contradiction) for "
    "a claim. They are not produced by the misinformation-classification "
    "model and do not, by themselves, prove a claim true or false."
)


class EvidenceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    source: str
    url: str | None
    evidence_type: str
    description: str
    event_timestamp: datetime | None
    matched_confidence: float
    created_at: datetime
