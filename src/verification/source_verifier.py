"""
Stage 6 -- Official-source verification.

READ THIS FIRST: your spec lists PIB Fact Check, Google Fact Check, NDMA,
IMD, and State Disaster Management Authorities as potential sources. NONE of
those are wired in here -- there is no live API integration in this
project. What this module actually does is check a new claim against your
STORED corpus of TRUE-labeled IFND disaster claims (the same 894/1002-row
dataset from Stage 1/2), using TF-IDF cosine similarity, and reports whether
something similar is already "on record" as verified news.

This is explicitly the "research prototype using stored datasets rather
than real-time APIs" version your spec allows for Stage 6. Calling this
"official verification" without this caveat would overstate what it does --
it verifies against your dataset, not against NDMA/IMD/PIB in real time.
"""
import os
import pandas as pd
from dataclasses import dataclass
from typing import Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

DATA_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "data", "processed", "ifnd_disaster_located.parquet"
)
MATCH_THRESHOLD = 0.35  # cosine similarity above this counts as "a record found"


@dataclass
class VerificationResult:
    matched: bool
    similarity: float
    matched_claim: Optional[str]
    matched_label: Optional[str]
    source_note: str = (
        "Checked against stored IFND corpus only -- no live NDMA/IMD/PIB "
        "Fact Check integration exists yet."
    )


class SourceVerifier:
    def __init__(self, data_path: str = DATA_PATH):
        df = pd.read_parquet(data_path)
        # verify against the TRUE-labeled subset specifically -- that's the
        # closest stand-in this project has for "confirmed by a real source"
        self.reference_df = df[df["Label"] == "TRUE"].reset_index(drop=True)
        self.vectorizer = TfidfVectorizer(max_features=5000, ngram_range=(1, 2), stop_words="english")
        self.reference_matrix = self.vectorizer.fit_transform(self.reference_df["Statement"])

    def verify(self, text: str) -> VerificationResult:
        query_vec = self.vectorizer.transform([text])
        sims = cosine_similarity(query_vec, self.reference_matrix)[0]
        best_idx = sims.argmax()
        best_sim = float(sims[best_idx])

        if best_sim >= MATCH_THRESHOLD:
            return VerificationResult(
                matched=True,
                similarity=best_sim,
                matched_claim=self.reference_df.iloc[best_idx]["Statement"],
                matched_label="TRUE",
            )
        return VerificationResult(matched=False, similarity=best_sim, matched_claim=None, matched_label=None)


if __name__ == "__main__":
    verifier = SourceVerifier()
    samples = [
        "5 more die as flood situation in Assam remains critical",       # should be near-identical to a real row
        "Aliens landed in Whitefield Bengaluru and caused the flood",     # should find nothing
    ]
    for s in samples:
        r = verifier.verify(s)
        print(f"\n{s}")
        print(f"  matched={r.matched}  similarity={r.similarity:.2f}")
        if r.matched:
            print(f"  closest record: {r.matched_claim}")
