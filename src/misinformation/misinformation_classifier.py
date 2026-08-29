"""
Misinformation detection -- wraps your EXISTING trained baseline
(outputs/baseline_a_disaster_only.joblib + vectorizer) behind a reusable
`.predict(text)` interface. No retraining happens here; this file loads
what build_baseline.py already produced.

Design note (same pattern as Stage 2 and Stage 3): `MisinformationClassifier`
is the interface. `TfidfLogRegClassifier` is today's working implementation.
Below it are three CLEARLY UNIMPLEMENTED stub classes for the models your
spec lists as future upgrades -- MuRIL, IndicBERT/XLM-R, and an LLM-based
comparison. They exist so the shape of the upgrade path is visible in the
code and explainable in a viva, but they raise NotImplementedError on
purpose: installing transformers/torch and downloading model weights is a
real jump in complexity, and your spec says not to make that jump yet.
"""
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Tuple, Optional
import joblib

OUTPUTS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "outputs")
MODEL_PATH = os.path.join(OUTPUTS_DIR, "baseline_a_disaster_only.joblib")
VECTORIZER_PATH = os.path.join(OUTPUTS_DIR, "baseline_a_vectorizer.joblib")


@dataclass
class MisinformationResult:
    label: str                                  # "TRUE", "FAKE", or "UNVERIFIED" -- see verdict logic below
    confidence: float                            # probability of the predicted label, 0-1
    prob_true: float                              # raw P(true), for reference regardless of label
    model_name: str
    top_terms: List[Tuple[str, float]] = field(default_factory=list)  # (term, contribution), signed

# ---- Stage 5: TRUE / FAKE / UNVERIFIED -----------------------------------
# IMPORTANT, read before changing this: IFND has no genuine UNVERIFIED
# examples -- it's a 2-class (TRUE/Fake) dataset. There is no ground truth
# to validate a 3-class model against, so this is NOT a trained 3rd class.
# It's an OPERATIONAL rule layered on top of the existing 2-class model's
# own confidence, per your spec's explicit instruction: "If reliable data
# for UNVERIFIED is unavailable, clearly explain an operational definition
# rather than pretending it is ground truth." This is that definition:
#
#   If the model's own confidence is below UNVERIFIED_CONFIDENCE_THRESHOLD,
#   report UNVERIFIED instead of forcing a TRUE/FAKE call.
#
# In plain terms: UNVERIFIED here means "the model itself isn't sure,"
# not "we checked and couldn't confirm it." A real UNVERIFIED (per Stage 6)
# would ideally also mean "no matching official source was found either
# way" -- that's wired in at the pipeline level in analyze_claim.py, not
# here, because this classifier has no access to the verification corpus.
UNVERIFIED_CONFIDENCE_THRESHOLD = 0.65


def apply_verdict(prob_true: float) -> Tuple[str, float]:
    """Turns a raw P(true) into (label, confidence) including the
    operational UNVERIFIED band. Confidence is always P(the reported label)."""
    confidence = prob_true if prob_true >= 0.5 else 1 - prob_true
    if confidence < UNVERIFIED_CONFIDENCE_THRESHOLD:
        return "UNVERIFIED", confidence
    return ("TRUE" if prob_true >= 0.5 else "FAKE"), confidence


class MisinformationClassifier(ABC):
    @abstractmethod
    def predict(self, text: str) -> MisinformationResult:
        raise NotImplementedError


class TfidfLogRegClassifier(MisinformationClassifier):
    """Your Stage 1 baseline (894-row disaster subset, 98.9% test accuracy --
    remember the source-leakage caveat from STATUS.md when you quote that
    number). Loads the already-trained model; does not retrain."""

    def __init__(self, model_path: str = MODEL_PATH, vectorizer_path: str = VECTORIZER_PATH):
        self.clf = joblib.load(model_path)
        self.vec = joblib.load(vectorizer_path)
        self.feature_names = self.vec.get_feature_names_out()

    def predict(self, text: str) -> MisinformationResult:
        X = self.vec.transform([text])
        prob_true = float(self.clf.predict_proba(X)[0][1])
        label, confidence = apply_verdict(prob_true)

        # explainability: which words in THIS text pushed the prediction which way
        row = X.tocoo()
        contributions = [
            (self.feature_names[col], float(val) * float(self.clf.coef_[0][col]))
            for col, val in zip(row.col, row.data)
        ]
        contributions.sort(key=lambda t: abs(t[1]), reverse=True)

        return MisinformationResult(
            label=label,
            confidence=confidence,
            prob_true=prob_true,
            model_name="TF-IDF + Logistic Regression (baseline_a)",
            top_terms=contributions[:6],
        )


# ---- future upgrade path (Stage 4 spec items 2 and 3) -- not implemented yet ----

class MuRILClassifier(MisinformationClassifier):
    """Placeholder for a MuRIL (Multilingual Representations for Indian
    Languages) fine-tune. Needed once you have Hindi/regional-language data
    from Reddit/Telegram -- the current baseline is English-only, trained on
    an English-only dataset (see STATUS.md). Would need: transformers, torch,
    a fine-tuning script, and labeled non-English data that doesn't exist yet."""
    def predict(self, text: str) -> MisinformationResult:
        raise NotImplementedError("MuRIL not wired in yet -- needs labeled multilingual data first")


class TransformerClassifier(MisinformationClassifier):
    """Placeholder for IndicBERT or XLM-R, same reasoning as MuRIL above."""
    def predict(self, text: str) -> MisinformationResult:
        raise NotImplementedError("IndicBERT/XLM-R not wired in yet")


class LLMComparisonClassifier(MisinformationClassifier):
    """Placeholder for a zero-shot LLM baseline (e.g. via API), useful as a
    comparison point against the fine-tuned models above in your report --
    not a replacement for either."""
    def predict(self, text: str) -> MisinformationResult:
        raise NotImplementedError("LLM comparison baseline not wired in yet")


if __name__ == "__main__":
    clf = TfidfLogRegClassifier()
    samples = [
        "5 more die as flood situation in Assam remains critical",
        "Old video of 2019 Kerala floods being shared as visuals from the current Assam flooding",
        "Heavy rain causes flooding in Whitefield, Bengaluru",
    ]
    for s in samples:
        r = clf.predict(s)
        print(f"\n{s}")
        print(f"  label={r.label}  confidence={r.confidence:.2%}  (P(true)={r.prob_true:.2%})")
        print(f"  top terms: {[(t, round(c,2)) for t, c in r.top_terms]}")
