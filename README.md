# HMT — Hyperlocal Misinformation Tracker for Disaster Relief

A research prototype (not a live system) that takes a disaster-related claim and returns a disaster type, resolved location, TRUE/FAKE/UNVERIFIED verdict, and a priority score. Built incrementally, stage by stage — see below for what each stage actually does and its real, tested limitations.

## Quick start

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# analyze one claim from the command line
python3 run.py "Heavy rainfall has caused severe flooding in Whitefield, Bengaluru."

# or launch the dashboard
streamlit run dashboard/app.py
```

## What's real vs. what's a placeholder

| Stage | Module | Status |
|---|---|---|
| 1 | `src/build_baseline.py` | Real — TF-IDF + Logistic Regression trained on 894 IFND disaster claims |
| 2 | `src/disaster/` | Real — rule-based, 13 disaster type categories |
| 3 | `src/location/` | Real — real India Post gazetteer (39,734 localities), fuzzy matching |
| 4 | `src/misinformation/` | Real — wraps Stage 1's trained model; MuRIL/IndicBERT/LLM slots are `NotImplementedError` stubs, not real |
| 5 | `src/misinformation/misinformation_classifier.py` (verdict logic) | UNVERIFIED is an **operational rule** (low model confidence), not a trained 3rd class — IFND has no real UNVERIFIED ground truth |
| 6 | `src/verification/` | Checks against your **stored** IFND corpus via cosine similarity — **no live NDMA/IMD/PIB API**, despite the name "verification" |
| 7 | `src/utils/priority_scorer.py` | Real — rule-based, additive, fully documented scoring |
| 8 | `dashboard/app.py` | Real Streamlit app, tested end-to-end (button clicks, both tabs) before shipping |

## Known limitations (be ready for these in your viva)

- **Reported accuracy (98.9%) is inflated** by source/style leakage in IFND — see the "Pinned Note" in `outputs/hmt_webapp.html` or `STATUS.md` for the full diagnosis.
- **English-only.** IFND turned out to have no Hindi/regional-language content despite its reputation.
- **UNVERIFIED is a confidence threshold, not a real third class.** See the comment block in `misinformation_classifier.py`.
- **Stage 6 "verification" checks your own dataset, not live government sources.** No PIB/NDMA/IMD API integration exists.
- **Location extraction has known false-positive classes** — common English words that coincidentally match real place names (documented in `location_extractor.py`), and any locality-level name not in the 2017-vintage gazetteer will simply not resolve.
- **Priority thresholds are a judgment call**, not learned from data.

## Full history

`STATUS.md` and `DATA_SOURCES.md` have the detailed session-by-session log, including every bug found and fixed during testing (there were several — regex plural bugs, city-rename collisions, nondeterministic ordering, a `.capitalize()` string bug) and the reasoning behind each fix.

## Project structure

```
hyperlocal-misinfo-tracker/
├── data/{raw,external,processed}/
├── outputs/                  # trained models, evaluation artifacts, demo HTML
├── src/
│   ├── disaster/             # Stage 2
│   ├── location/             # Stage 3
│   ├── misinformation/       # Stage 4 + 5
│   ├── verification/         # Stage 6
│   ├── utils/                # Stage 7
│   ├── analyze_claim.py      # combined pipeline
│   ├── eda_ifnd.py           # Stage 1
│   └── build_baseline.py     # Stage 1
├── dashboard/app.py           # Stage 8
├── run.py                     # CLI entry point
└── requirements.txt
```

## Not built (deliberately, per project scope)

- Live Reddit/Telegram ingestion (needs your API credentials)
- Real government API integration for Stage 6
- MuRIL/IndicBERT fine-tuning (needs multilingual labeled data that doesn't exist yet)
- A real geographic map beyond state-level centroids (gazetteer has no coordinates)
