"""EDA on the raw IFND.csv dataset."""
import pandas as pd
import re

try:
    df = pd.read_csv("/home/claude/hyperlocal-misinfo-tracker/data/raw/IFND.csv", encoding="utf-8")
except UnicodeDecodeError:
    df = pd.read_csv("/home/claude/hyperlocal-misinfo-tracker/data/raw/IFND.csv", encoding="latin-1")
    print("NOTE: fell back to latin-1 encoding\n")

print("=== Shape ===")
print(df.shape)

print("\n=== Columns / dtypes ===")
print(df.dtypes)

print("\n=== Nulls per column ===")
print(df.isna().sum())

print("\n=== Label distribution ===")
print(df["Label"].value_counts(dropna=False))

print("\n=== Category distribution (top 30) ===")
print(df["Category"].value_counts(dropna=False).head(30))

print("\n=== Web (source) distribution (top 20) ===")
print(df["Web"].value_counts(dropna=False).head(20))

print("\n=== Date range (raw sample) ===")
print(df["Date"].dropna().unique()[:20])

# crude Hindi/Devanagari detection to check claimed bilinguality
devanagari_re = re.compile(r"[\u0900-\u097F]")
df["has_devanagari"] = df["Statement"].fillna("").apply(lambda t: bool(devanagari_re.search(t)))
print("\n=== Devanagari (Hindi script) presence in Statement ===")
print(df["has_devanagari"].value_counts())

# disaster-relevance keyword scan (English + transliterated Hindi terms)
disaster_kw = [
    "flood", "cyclone", "earthquake", "landslide", "tsunami", "disaster",
    "rescue", "relief", "evacuat", "cloudburst", "heavy rain", "storm",
    "quake", "drought", "wildfire", "avalanche", "IMD", "NDMA", "SDMA",
]
pattern = re.compile("|".join(disaster_kw), re.IGNORECASE)
df["disaster_related"] = df["Statement"].fillna("").apply(lambda t: bool(pattern.search(t)))
print("\n=== Disaster-related (keyword match) count ===")
print(df["disaster_related"].value_counts())

print("\n=== Label distribution WITHIN disaster-related subset ===")
print(df[df["disaster_related"]]["Label"].value_counts())

print("\n=== Category distribution WITHIN disaster-related subset (top 15) ===")
print(df[df["disaster_related"]]["Category"].value_counts().head(15))

print("\n=== Sample disaster-related rows ===")
sample = df[df["disaster_related"]][["Statement", "Category", "Label", "Date"]].sample(
    min(10, df["disaster_related"].sum()), random_state=42
)
for _, row in sample.iterrows():
    print(f"- [{row['Label']}] ({row['Category']}, {row['Date']}) {row['Statement'][:120]}")

df.to_parquet("/home/claude/hyperlocal-misinfo-tracker/data/processed/ifnd_annotated.parquet")
print("\nSaved annotated parquet to data/processed/ifnd_annotated.parquet")
