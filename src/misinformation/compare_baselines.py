"""
Compares Logistic Regression (the shipped baseline), Random Forest, and a
linear-kernel SVM on the SAME 894-row disaster subset, SAME train/test
split, and SAME TF-IDF feature space that src/build_baseline.py already
used for Baseline A -- so any performance difference between the three is
attributable to the algorithm, not to a different split or vectorizer.
Reproducing the exact split/vectorizer is verified by checking the
reproduced Logistic Regression numbers against
outputs/baseline_results_summary.json's existing Baseline A figures before
trusting the RF/SVM comparison at all (see MODEL_EVALUATION.md).

Model-selection rule (a judgment call, stated as one, same style as
utils/priority_scorer.py's thresholds): pick by macro F1, not raw accuracy
-- the 512 TRUE / 382 FAKE split is imbalanced enough that accuracy alone
would flatter whichever class is more common. A challenger must beat the
shipped Logistic Regression's macro F1 by >= CHALLENGER_MARGIN to replace
it; ties/small gains stay with Logistic Regression, which is already
shipped, already documented at length (see STATUS.md's leakage diagnosis),
and -- together with the linear SVM -- supports the same per-instance,
signed coefficient-based `top_terms` explainability that
TfidfLogRegClassifier.predict() already provides. Random Forest has no
`.coef_`; if it ever wins by a clear margin, only ship it with an
explicitly caveated `feature_importances_`-based top_terms fallback
(global importance, not this specific claim's contribution) -- never
silently drop explainability.

IMPORTANT: if this script ever results in a different shipped model, every
quoted accuracy number in README.md/STATUS.md must be updated in the SAME
change, and the source/style-leakage finding re-stated as a property of
the IFND dataset (not something a different algorithm "fixes") -- see
STATUS.md section 2.
"""
import json
import os

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC

DATA_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "data", "processed", "ifnd_disaster_subset.parquet"
)
OUTPUTS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "outputs")
RESULTS_PATH = os.path.join(OUTPUTS_DIR, "baseline_comparison_results.json")

CHALLENGER_MARGIN = 0.01
RANDOM_STATE = 42


def _metrics(y_test, y_pred) -> dict:
    report = classification_report(y_test, y_pred, target_names=["FAKE", "TRUE"], output_dict=True)
    cm = confusion_matrix(y_test, y_pred).tolist()
    return {
        "accuracy": report["accuracy"],
        "macro_f1": report["macro avg"]["f1-score"],
        "weighted_f1": report["weighted avg"]["f1-score"],
        "fake_precision": report["FAKE"]["precision"],
        "fake_recall": report["FAKE"]["recall"],
        "fake_f1": report["FAKE"]["f1-score"],
        "true_precision": report["TRUE"]["precision"],
        "true_recall": report["TRUE"]["recall"],
        "true_f1": report["TRUE"]["f1-score"],
        "confusion_matrix": cm,  # rows/cols ordered [FAKE, TRUE]
    }


def select_winner(macro_f1_by_model: dict, margin: float = CHALLENGER_MARGIN) -> str:
    """Pure selection-rule function, kept separate from model training so
    it can be unit-tested deterministically (real sklearn training on tiny
    synthetic data can't reliably force a specific model to "win" by a
    controlled margin). `macro_f1_by_model` must contain the key
    "logistic_regression"; a challenger key wins only if it beats
    logistic_regression's macro F1 by >= `margin`, and the highest-scoring
    qualifying challenger is picked if more than one clears the bar."""
    baseline = macro_f1_by_model["logistic_regression"]
    winner = "logistic_regression"
    for name, score in macro_f1_by_model.items():
        if name == "logistic_regression":
            continue
        if score - baseline >= margin and score > macro_f1_by_model[winner]:
            winner = name
    return winner


def run_comparison(df: pd.DataFrame | None = None) -> dict:
    """Runs the full comparison. `df` is injectable for tests (small
    synthetic data); defaults to the real 894-row disaster subset."""
    if df is None:
        df = pd.read_parquet(DATA_PATH)

    X_train, X_test, y_train, y_test = train_test_split(
        df["Statement"], df["y"], test_size=0.2,
        random_state=RANDOM_STATE, stratify=df["y"],
    )

    vectorizer = TfidfVectorizer(max_features=8000, ngram_range=(1, 2), min_df=2, stop_words="english")
    Xtr = vectorizer.fit_transform(X_train)
    Xte = vectorizer.transform(X_test)

    models = {
        "logistic_regression": LogisticRegression(max_iter=1000, class_weight="balanced"),
        "random_forest": RandomForestClassifier(
            n_estimators=300, class_weight="balanced", random_state=RANDOM_STATE
        ),
        # linear kernel (not rbf) specifically so .coef_ stays available --
        # needed for the same per-instance top_terms explainability trick
        # TfidfLogRegClassifier already does. probability=True is needed
        # for apply_verdict()'s confidence-threshold logic.
        "svm_linear": SVC(kernel="linear", probability=True, class_weight="balanced", random_state=RANDOM_STATE),
    }

    results = {}
    for name, model in models.items():
        model.fit(Xtr, y_train)
        pred = model.predict(Xte)
        results[name] = _metrics(y_test, pred)
        results[name]["model_object"] = model  # stripped before JSON dump, used for artifact saving below

    baseline_macro_f1 = results["logistic_regression"]["macro_f1"]
    winner = select_winner({name: r["macro_f1"] for name, r in results.items()})

    summary = {
        "dataset": {
            "path": "data/processed/ifnd_disaster_subset.parquet",
            "n_rows": len(df),
            "train_size": len(X_train),
            "test_size": len(X_test),
            "random_state": RANDOM_STATE,
        },
        "vectorizer": {"max_features": 8000, "ngram_range": [1, 2], "min_df": 2, "stop_words": "english"},
        "selection_rule": (
            f"Pick by macro F1. A challenger must beat logistic_regression's "
            f"macro F1 by >= {CHALLENGER_MARGIN} to be adopted; otherwise "
            f"logistic_regression ships (see this script's module docstring)."
        ),
        "models": {name: {k: v for k, v in r.items() if k != "model_object"} for name, r in results.items()},
        "winner": winner,
        "margin_over_logreg": results[winner]["macro_f1"] - baseline_macro_f1,
    }

    return summary, results, vectorizer


def save_artifacts(summary: dict, results: dict, vectorizer) -> None:
    os.makedirs(OUTPUTS_DIR, exist_ok=True)
    with open(RESULTS_PATH, "w") as f:
        json.dump(summary, f, indent=2)

    winner = summary["winner"]
    if winner != "logistic_regression":
        joblib.dump(results[winner]["model_object"], os.path.join(OUTPUTS_DIR, f"baseline_{winner}.joblib"))
        joblib.dump(vectorizer, os.path.join(OUTPUTS_DIR, f"baseline_{winner}_vectorizer.joblib"))


if __name__ == "__main__":
    summary, results, vectorizer = run_comparison()
    save_artifacts(summary, results, vectorizer)

    print(json.dumps(summary, indent=2))
    print(f"\nWinner: {summary['winner']} (margin over logistic_regression: {summary['margin_over_logreg']:.4f})")

    logreg_from_baseline_a = json.load(open(os.path.join(OUTPUTS_DIR, "baseline_results_summary.json")))
    reproduced = summary["models"]["logistic_regression"]
    original = logreg_from_baseline_a["baseline_A_disaster_only_trained"]
    print("\n--- Reproduction sanity check vs. outputs/baseline_results_summary.json ---")
    print(f"  original accuracy={original['accuracy']:.4f}  reproduced accuracy={reproduced['accuracy']:.4f}")
    print(f"  original macro_f1={original['macro_f1']:.4f}  reproduced macro_f1={reproduced['macro_f1']:.4f}")
