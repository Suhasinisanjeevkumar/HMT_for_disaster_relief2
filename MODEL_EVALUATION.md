# Model Evaluation — Misinformation Classifier

## Reproduce this

```bash
python3 src/misinformation/compare_baselines.py
```

Writes `outputs/baseline_comparison_results.json` (the exact numbers below). All three models are trained on the
**identical** train/test split and TF-IDF feature space, so any performance delta is attributable to the
algorithm, not to a different split or vectorizer — see `src/misinformation/compare_baselines.py`'s module
docstring for the full reasoning.

## Dataset

| | |
|---|---|
| Source | `data/processed/ifnd_disaster_subset.parquet` — the 894-row disaster-relevant subset of IFND (56,714 rows), refined via a keyword filter (see `src/build_baseline.py`) |
| Classes | TRUE (512) / Fake (382) |
| Split | 80/20 stratified, `random_state=42` — train 715, test 179 |
| Features | TF-IDF, `max_features=8000`, `ngram_range=(1,2)`, `min_df=2`, English stopwords removed |

## Results

| Model | Accuracy | Macro F1 | Weighted F1 | FAKE Precision/Recall/F1 | TRUE Precision/Recall/F1 |
|---|---|---|---|---|---|
| **Logistic Regression** (shipped) | 0.9888 | 0.9885 | 0.9888 | 1.000 / 0.974 / 0.987 | 0.981 / 1.000 / 0.990 |
| Random Forest (300 trees) | 0.9888 | 0.9885 | 0.9888 | 1.000 / 0.974 / 0.987 | 0.981 / 1.000 / 0.990 |
| Linear SVM | 0.9944 | 0.9943 | 0.9944 | 1.000 / 0.987 / 0.993 | 0.990 / 1.000 / 0.995 |

Confusion matrices (rows/cols ordered [FAKE, TRUE], test set n=179):

```
Logistic Regression        Random Forest              Linear SVM
         FAKE  TRUE                FAKE  TRUE                 FAKE  TRUE
FAKE  [   74     2 ]      FAKE  [   74     2 ]      FAKE  [   75     1 ]
TRUE  [    0   103 ]      TRUE  [    0   103 ]      TRUE  [    0   103 ]
```

## Selection rule and outcome

**Rule** (a judgment call, stated as one — see `compare_baselines.py`'s `select_winner()`): pick by macro F1, not
raw accuracy, since the 512/382 class split is imbalanced enough that accuracy alone would flatter the majority
class. A challenger must beat Logistic Regression's macro F1 by **≥ 0.01** to be adopted.

**Outcome: Logistic Regression ships, unchanged.** Random Forest tied it exactly (0.9885 macro F1 both). The
linear SVM genuinely scored higher (0.9943 vs. 0.9885, a real +0.0057 improvement) but that margin **did not clear
the 0.01 threshold**, so the rule kept the incumbent. This is a real, reproducible result, not a foregone
conclusion the rule was tuned to produce after the fact — the margin was checked, not assumed.

A secondary reason favoring Logistic Regression if the margin had been closer: it (and the linear SVM) support
the same per-instance, signed-coefficient `top_terms` explainability that `TfidfLogRegClassifier.predict()`
already provides. Random Forest has no `.coef_` — only global `.feature_importances_`, which cannot explain *this
specific claim's* prediction the way a coefficient dot-product can. If a future run ever has Random Forest clear
the adoption margin, it should only ship with an explicitly caveated "global importance, not this claim's
specific contribution" explainability fallback, not silently dropped explainability.

## The leakage finding still applies

**Read this before quoting any of the numbers above as "the model's real-world accuracy."** `STATUS.md`
documents that IFND's `Web` (source) column and fact-check-boilerplate words ("fact", "check", "video", "shared",
"viral") predict the label almost perfectly by themselves — the original diagnosis found the classifier was
partly learning to recognize *fact-check article headline formatting*, not the underlying truth of a claim. That
finding is a property of the **IFND dataset**, not of Logistic Regression specifically — switching to Random
Forest or a linear SVM does not fix it, and neither would switch away from it if adopted. The real test of
generalization would be evaluation on freshly-collected Reddit/Telegram data with no fact-check-style framing,
which this project does not have (see `STATUS.md`, "What I need from you to keep going").

## What was deliberately not attempted

Transformer fine-tuning (MuRIL, IndicBERT, XLM-R) or an LLM-based comparison classifier — no labeled multilingual
data exists for this project (IFND turned out to be English-only despite its reputation), and fine-tuning without
labeled data isn't meaningful. These stay as `NotImplementedError` stubs in
`src/misinformation/misinformation_classifier.py`, visible in the code as a real upgrade path rather than
silently absent.
