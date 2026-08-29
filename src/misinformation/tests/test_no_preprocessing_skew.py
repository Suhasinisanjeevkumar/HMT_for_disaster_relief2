"""
Regression guard for the risk documented in
src/preprocessing/text_preprocessor.py's module docstring: nothing should
ever insert new text cleaning ahead of TfidfLogRegClassifier.predict(),
since the model was fit on raw IFND text. This pins the model's output for
a fixed input as a golden value -- if this test ever fails, either the
shipped model changed (expected only via a deliberate compare_baselines.py
swap, see MODEL_EVALUATION.md) or something started preprocessing text
ahead of .transform() (not expected, ever, without a retrain).
"""
from misinformation.misinformation_classifier import TfidfLogRegClassifier

SAMPLE = "Heavy rain causes flooding in Whitefield, Bengaluru"


def test_prediction_is_deterministic_and_unpreprocessed():
    clf = TfidfLogRegClassifier()
    r = clf.predict(SAMPLE)
    assert r.label == "TRUE"
    assert abs(r.confidence - 0.7932724023186841) < 1e-9
