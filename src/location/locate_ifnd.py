import sys, os
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from location.location_extractor import GazetteerLocationExtractor

IN_PATH = "/home/claude/hyperlocal-misinfo-tracker/data/processed/ifnd_disaster_typed.parquet"
OUT_PATH = "/home/claude/hyperlocal-misinfo-tracker/data/processed/ifnd_disaster_located.parquet"

df = pd.read_parquet(IN_PATH)
extractor = GazetteerLocationExtractor()

levels, states, cities = [], [], []
for text in df["Statement"]:
    res = extractor.extract(text)
    best = res.best
    levels.append(best.match_level if best else "none")
    states.append(best.state if best else None)
    cities.append(best.city if best else None)

df["location_level"] = levels
df["location_state"] = states
df["location_city"] = cities
df.to_parquet(OUT_PATH)

print(f"Total claims: {len(df)}")
print(df["location_level"].value_counts())
print(f"\nResolved (any level): {(df['location_level'] != 'none').sum()} "
      f"({(df['location_level'] != 'none').mean()*100:.1f}%)")

print("\nTop 10 states by claim count (of resolved claims):")
print(df["location_state"].value_counts().head(10))

print("\nSample locality-level resolutions:")
loc_rows = df[df["location_level"] == "locality"][["Statement", "location_city", "location_state"]]
for _, r in loc_rows.head(6).iterrows():
    print(f"  [{r['location_city']}, {r['location_state']}] {r['Statement'][:80]}")
