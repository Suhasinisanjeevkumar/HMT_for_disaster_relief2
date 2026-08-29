"""
Build a refined disaster-relevant subset of IFND and train two baselines:
  (A) classifier trained ONLY on the disaster-relevant subset
  (B) classifier trained on the FULL dataset, evaluated on disaster subset (domain-shift check)
"""
import re
import json
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix
import joblib

RAW = "/home/claude/hyperlocal-misinfo-tracker/data/raw/IFND.csv"
OUT_DIR = "/home/claude/hyperlocal-misinfo-tracker/data/processed"
MODEL_DIR = "/home/claude/hyperlocal-misinfo-tracker/outputs"

df = pd.read_csv(RAW, encoding="latin-1")
df = df.dropna(subset=["Statement", "Label"])
df["y"] = (df["Label"].str.strip().str.upper() == "TRUE").astype(int)  # 1=true, 0=fake

# --- refined disaster-relevance filter ---
# unambiguous disaster nouns (safe on their own)
strong_terms = [
    "flood", "cyclone", "earthquake", "landslide", "tsunami", "cloudburst",
    "wildfire", "avalanche", "drought", "quake", "tremor",
]
# phrases that need more context to avoid false positives (political "storm", hostage "rescue")
phrase_terms = [
    "rescue operation", "relief camp", "relief fund", "evacuat", "disaster management",
    "flood warning", "cyclone warning", "landslide warning", "heavy rainfall",
    "heavy rain", "flood situation", "flood-hit", "flash flood", "storm surge",
    "imd warning", "ndma", "sdma", "red alert weather", "orange alert weather",
    "death toll rises", "rescue team", "rescue teams", "search and rescue",
]
pattern = re.compile("|".join(strong_terms + phrase_terms), re.IGNORECASE)
df["disaster_related"] = df["Statement"].apply(lambda t: bool(pattern.search(str(t))))

disaster_df = df[df["disaster_related"]].copy()
print(f"Refined disaster-relevant subset: {len(disaster_df)} rows "
      f"(TRUE={int((disaster_df.y==1).sum())}, FAKE={int((disaster_df.y==0).sum())})")

disaster_df.to_parquet(f"{OUT_DIR}/ifnd_disaster_subset.parquet")

# =========================================================================
# Baseline A: train + eval on disaster subset only
# =========================================================================
X_train, X_test, y_train, y_test = train_test_split(
    disaster_df["Statement"], disaster_df["y"], test_size=0.2,
    random_state=42, stratify=disaster_df["y"]
)

vec_a = TfidfVectorizer(max_features=8000, ngram_range=(1, 2), min_df=2, stop_words="english")
Xtr_a = vec_a.fit_transform(X_train)
Xte_a = vec_a.transform(X_test)

clf_a = LogisticRegression(max_iter=1000, class_weight="balanced")
clf_a.fit(Xtr_a, y_train)
pred_a = clf_a.predict(Xte_a)

report_a = classification_report(y_test, pred_a, target_names=["FAKE", "TRUE"], output_dict=True)
print("\n=== Baseline A: trained + evaluated on disaster-only subset ===")
print(classification_report(y_test, pred_a, target_names=["FAKE", "TRUE"]))
print("Confusion matrix:\n", confusion_matrix(y_test, pred_a))

joblib.dump(clf_a, f"{MODEL_DIR}/baseline_a_disaster_only.joblib")
joblib.dump(vec_a, f"{MODEL_DIR}/baseline_a_vectorizer.joblib")

# =========================================================================
# Baseline B: train on FULL dataset (general fake news), eval on disaster subset
# (domain-shift check -- does a general classifier generalize to disaster claims?)
# =========================================================================
full_train_df, general_test_df = train_test_split(
    df, test_size=0.2, random_state=42, stratify=df["y"]
)
# make sure the disaster-subset test rows used above aren't leaking into training
full_train_df = full_train_df[~full_train_df.index.isin(X_test.index)]

vec_b = TfidfVectorizer(max_features=20000, ngram_range=(1, 2), min_df=2, stop_words="english")
Xtr_b = vec_b.fit_transform(full_train_df["Statement"])
clf_b = LogisticRegression(max_iter=1000, class_weight="balanced")
clf_b.fit(Xtr_b, full_train_df["y"])

# evaluate B on the SAME disaster-only test split used for A (apples-to-apples)
Xte_b_on_disaster = vec_b.transform(X_test)
pred_b_on_disaster = clf_b.predict(Xte_b_on_disaster)

report_b = classification_report(y_test, pred_b_on_disaster, target_names=["FAKE", "TRUE"], output_dict=True)
print("\n=== Baseline B: trained on FULL dataset, evaluated on the SAME disaster-only test set ===")
print(classification_report(y_test, pred_b_on_disaster, target_names=["FAKE", "TRUE"]))
print("Confusion matrix:\n", confusion_matrix(y_test, pred_b_on_disaster))

joblib.dump(clf_b, f"{MODEL_DIR}/baseline_b_general.joblib")
joblib.dump(vec_b, f"{MODEL_DIR}/baseline_b_vectorizer.joblib")

# =========================================================================
# save a compact results summary
# =========================================================================
summary = {
    "disaster_subset_size": len(disaster_df),
    "disaster_subset_label_counts": disaster_df["Label"].value_counts().to_dict(),
    "baseline_A_disaster_only_trained": {
        "test_size": len(X_test),
        "macro_f1": report_a["macro avg"]["f1-score"],
        "accuracy": report_a["accuracy"],
        "fake_f1": report_a["FAKE"]["f1-score"],
        "true_f1": report_a["TRUE"]["f1-score"],
    },
    "baseline_B_general_trained_eval_on_disaster": {
        "test_size": len(X_test),
        "macro_f1": report_b["macro avg"]["f1-score"],
        "accuracy": report_b["accuracy"],
        "fake_f1": report_b["FAKE"]["f1-score"],
        "true_f1": report_b["TRUE"]["f1-score"],
    },
}
with open(f"{MODEL_DIR}/baseline_results_summary.json", "w") as f:
    json.dump(summary, f, indent=2)

print("\n=== SUMMARY ===")
print(json.dumps(summary, indent=2))
