from pydantic import BaseModel


class OverviewStats(BaseModel):
    total_claims: int
    true_count: int
    fake_count: int
    unverified_count: int
    high_priority_count: int
    verified_against_corpus_count: int
    verification_rate: float  # verified_against_corpus_count / total_claims


class CountItem(BaseModel):
    label: str
    count: int


class TimelinePoint(BaseModel):
    date: str  # YYYY-MM-DD (day bucket)
    count: int
