"""
Runs the Stage 2 disaster classifier over the full IFND dataset, producing
per-row disaster_types / primary_type columns, and compares the resulting
"is disaster related" count against Stage 1's binary filter (894 rows) so
we know exactly what changed and why -- no silent drift.
"""
import sys
import os
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from disaster.disaster_classifier import KeywordDisasterClassifier

RAW = "/home/claude/hyperlocal-misinfo-tracker/data/raw/IFND.csv"
OUT_PARQUET = "/home/claude/hyperlocal-misinfo-tracker/data/processed/ifnd_disaster_typed.parquet"
OLD_SUBSET = "/home/claude/hyperlocal-misinfo-tracker/data/processed/ifnd_disaster_subset.parquet"

df = pd.read_csv(RAW, encoding="latin-1")
df = df.dropna(subset=["Statement", "Label"])
df["y"] = (df["Label"].str.strip().str.upper() == "TRUE").astype(int)

clf = KeywordDisasterClassifier()
results = df["Statement"].apply(clf.classify)

df["is_disaster_related"] = results.apply(lambda r: r.is_disaster_related)
df["disaster_types"] = results.apply(lambda r: r.disaster_types)
df["primary_type"] = results.apply(lambda r: r.primary_type)

new_subset = df[df["is_disaster_related"]].copy()
new_subset.to_parquet(OUT_PARQUET)

print(f"New (Stage 2, typed) disaster-relevant subset: {len(new_subset)} rows")
print(f"  TRUE={int((new_subset.y==1).sum())}  FAKE={int((new_subset.y==0).sum())}")

old_subset = pd.read_parquet(OLD_SUBSET)
print(f"\nOld (Stage 1, binary) disaster-relevant subset: {len(old_subset)} rows")

old_ids = set(old_subset["id"]) if "id" in old_subset.columns else set(old_subset.index)
new_ids = set(new_subset["id"]) if "id" in new_subset.columns else set(new_subset.index)
added = new_ids - old_ids
removed = old_ids - new_ids
print(f"\nDiff vs Stage 1: +{len(added)} rows newly included, -{len(removed)} rows dropped")

print("\n=== Primary disaster type distribution (real counts) ===")
print(new_subset["primary_type"].value_counts())

print("\n=== Sample rows with multiple disaster types detected ===")
multi = new_subset[new_subset["disaster_types"].apply(len) > 1]
print(f"{len(multi)} of {len(new_subset)} rows matched more than one type")
for _, row in multi.head(5).iterrows():
    print(f"  {row['disaster_types']}: {row['Statement'][:90]}")
