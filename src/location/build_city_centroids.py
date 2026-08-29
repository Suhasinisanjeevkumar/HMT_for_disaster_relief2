"""
One-time (but rerunnable) data-prep script that builds
data/external/city_centroids.csv from GeoNames' free, CC-BY-4.0-licensed
"cities1000" dump (every populated place with >=1000 people, worldwide),
filtered to India and the top N cities by population.

This does NOT run at request time or at app startup -- geocode_lookup.py
only ever reads the committed CSV this script produces. Rerun this script
only if you want to refresh/expand the centroid dataset; it needs network
access, nothing else does.

Source: https://download.geonames.org/export/dump/ (cities1000.zip,
admin1CodesASCII.txt) -- CC BY 4.0, GeoNames.org.
"""
import csv
import io
import os
import urllib.request
import zipfile

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data", "external")
CITIES_URL = "https://download.geonames.org/export/dump/cities1000.zip"
ADMIN1_URL = "https://download.geonames.org/export/dump/admin1CodesASCII.txt"
TOP_N = 400


def _fetch(url: str) -> bytes:
    with urllib.request.urlopen(url, timeout=60) as resp:
        return resp.read()


def build():
    admin1_raw = _fetch(ADMIN1_URL).decode("utf-8")
    admin1_names = {}  # "IN.19" -> "Karnataka"
    for line in admin1_raw.splitlines():
        parts = line.split("\t")
        if len(parts) >= 2:
            admin1_names[parts[0]] = parts[1]

    cities_zip = zipfile.ZipFile(io.BytesIO(_fetch(CITIES_URL)))
    raw = cities_zip.read("cities1000.txt").decode("utf-8")

    india_rows = []
    for line in raw.splitlines():
        f = line.split("\t")
        # geonameid, name, asciiname, alternatenames, lat, lon, feature class,
        # feature code, country code, cc2, admin1, admin2, admin3, admin4,
        # population, elevation, dem, timezone, modification date
        if len(f) < 15 or f[8] != "IN":
            continue
        name, lat, lon, admin1_code, population = f[2], f[4], f[5], f[10], f[14]
        state = admin1_names.get(f"IN.{admin1_code}", "")
        if not state or not population.isdigit():
            continue
        india_rows.append((name, state, float(lat), float(lon), int(population)))

    india_rows.sort(key=lambda r: r[4], reverse=True)
    top = india_rows[:TOP_N]

    out_path = os.path.join(DATA_DIR, "city_centroids.csv")
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["city", "state", "lat", "lon", "population"])
        for name, state, lat, lon, pop in top:
            writer.writerow([name, state, lat, lon, pop])

    print(f"Wrote {len(top)} rows to {out_path}")


if __name__ == "__main__":
    build()
