# Project Status — as of this session

What follows is real, verified progress against your IFND.csv and three public benchmark datasets — not projections. Everything below actually ran.

## 1. What's done

### Data acquired and verified
| Dataset | Rows/items | What it is | Status |
|---|---|---|---|
| **IFND.csv** (yours) | 56,714 | Indian fake/true news headlines, 2015–2020 | Loaded, cleaned, EDA'd |
| **PHEME veracity** | 10,456 (1,312 true rumours, 1,090 false rumours, 8,054 non-rumours, 9 events) | Twitter rumour veracity benchmark | Downloaded + parsed |
| **HumAID** | 53,531 train / 7,793 dev / 15,160 test | 19 real disaster events, humanitarian-category labels | Downloaded (HF parquet) |
| **IDRISI** | ~20.5K human-labeled + ~57K silver, location-mention spans | Geo-resolution benchmark for crisis tweets | Cloned (215MB) |

### Baseline classifiers trained and evaluated (real numbers, not estimates)
Refined the disaster-relevance keyword filter (dropped ambiguous standalone words like "storm"/"rescue" that were pulling in political-riot and crime stories; kept unambiguous terms + contextual phrases). Result: **894 disaster-relevant rows** (512 TRUE / 382 Fake) out of 56,714.

- Baseline A (TF-IDF + Logistic Regression, trained and tested only on the disaster subset): **99% macro F1**
- Baseline B (same model trained on the full 56K dataset, evaluated on the same disaster-only test set): **98% macro F1**

## 2. The important finding — read this before you trust those numbers

That 99% is not a real skill measurement, and reporting it as your model's accuracy in the capstone would be a mistake I want to flag now rather than have a committee member catch later.

**What's actually happening:** IFND's `Web` (source) column predicts the label almost perfectly by itself — TRIBUNEINDIA, THESTATESMAN, and INDIANEXPRESS rows are 100% TRUE; AUGMENT and BOOMLIVE rows are 100% Fake. When I pulled the logistic regression's top weighted features, the words driving "FAKE" predictions were **"fact", "check", "video", "shared", "viral", "old", "image"** — i.e. the model learned to recognize *fact-check article headline formatting* ("Fact Check: Video Of X Shared As Y"), not the underlying truth of the claim. TRUE items just read like ordinary news headlines. The classifier is a source/genre detector wearing a misinformation-detector costume.

I re-ran it after stripping the obvious fact-check boilerplate phrases ("fact check", "claim:", "shared", "viral", "old video/image", etc.) — it dropped to 94% F1, still leaning heavily on "video/image/old/kerala" as top signals. That remaining signal isn't pure noise — "old footage recirculated as new disaster news" is a real and common misinformation pattern — but it's a narrow one, and 94% on this test set still doesn't tell you how the model will do on a plain Reddit comment or Telegram forward that has no fact-check-style framing at all.

**What this means for your plan:**
- Don't report the 99%/98% numbers as classifier performance in your writeup — report them alongside this diagnosis, or better, don't lead with them at all.
- The real evaluation has to happen on your **freshly collected Reddit/Telegram data** once you have it — that data won't have "Fact Check:" headline structure, so it's a much fairer test of whether the model generalizes.
- Worth adding to your methodology section as a finding, not hiding: *"we found that headline-style fake news datasets like IFND are prone to source/style leakage, which we diagnosed and controlled for."* That's a legitimate, citable methodological contribution — reviewers like seeing that a team caught this rather than reported inflated numbers.
- Practical fix for training: when you get real Reddit/Telegram data, resist the urge to only add PIB/fact-checker-style debunk text as your "false" examples — try to also capture the *original rumor as it circulated* (the tweet/post being debunked, not the debunking article), since that's what your deployed model actually needs to recognize.

## 3. One correction to the original roadmap

I'd suggested scraping **PIB Fact Check's website** (factcheck.pib.gov.in) as a source of labeled false claims. I checked it directly — it's a **citizen submission portal** (login-gated query form), not a browsable public archive of past fact-checks. PIB's actual fact-check output lives on X/Instagram/Telegram (`t.me/PIB_FactCheck`), not a scrapeable web database. Also worth noting: PIB's mandate is narrowly "claims about Government of India policies/schemes" — not general disaster misinformation, so it was always going to be a partial source at best.

**Better replacement sources**, given IFND itself already shows BOOMLIVE, FACTCRESCENDO, DIGITEYE, NEWSMETER, and THELOGICALINDIAN as fact-checker sources (so the genre is already represented in your bootstrap data): for *fresh* ongoing collection, check whether these outlets publish `ClaimReview`-tagged content — if so, the **Google Fact Check Tools API** (free, official, structured — see the script in the original roadmap) should surface them without any scraping. The Telegram channel `t.me/PIB_FactCheck` is also directly joinable via Telethon like any public channel, which is simpler than scraping their web portal anyway.

## 4. What I need from you to keep going

I can't authenticate as you, so these need your action:
1. **Reddit OAuth app** (client_id/secret) — apply at reddit.com/prefs/apps if you haven't already (flagged as urgent last time — status?)
2. **Telegram API credentials** (api_id/api_hash from my.telegram.org) — needed for both city/news channels and `t.me/PIB_FactCheck`
3. **Google Fact Check Tools API key** — free, instant, from Google Cloud Console

Once you have any of these, send them my way (or just tell me you've got them) and I'll write the actual collection runs against the real APIs rather than the generic skeleton scripts.

## 5. Files in this session's project folder
```
hyperlocal-misinfo-tracker/
├── data/
│   ├── raw/IFND.csv                          (your file)
│   ├── raw/pheme/                            (downloaded, 1.1GB — see DATA_SOURCES.md to re-fetch)
│   ├── raw/humaid/                           (downloaded, ~7MB)
│   ├── raw/IDRISI/                           (downloaded, 215MB — see DATA_SOURCES.md to re-fetch)
│   └── processed/
│       ├── ifnd_annotated.parquet            (full IFND + disaster-relevance flags)
│       └── ifnd_disaster_subset.parquet      (894-row refined disaster subset)
├── src/
│   ├── eda_ifnd.py
│   └── build_baseline.py                     (trains + diagnoses both baselines)
├── outputs/
│   ├── baseline_a_disaster_only.joblib / _vectorizer.joblib
│   ├── baseline_b_general.joblib / _vectorizer.joblib
│   └── baseline_results_summary.json
└── DATA_SOURCES.md                            (exact commands to re-download PHEME/HumAID/IDRISI)
```
