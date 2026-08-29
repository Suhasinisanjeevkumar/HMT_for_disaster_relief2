# Data sources — verified working download commands

These were tested and confirmed working in this session. No authentication needed for any of them.

## PHEME veracity dataset (1.1GB extracted)
```bash
curl -sL -o PHEME_veracity.tar.bz2 "https://ndownloader.figshare.com/files/11767817"
tar -xzf PHEME_veracity.tar.bz2   # despite the .bz2 extension, it's actually gzip
```
9 events: Charlie Hebdo, Ferguson, Germanwings crash, Gurlitt, Ottawa shooting, Prince Toronto,
Putin missing, Sydney siege, Ebola-Essien. Each rumour has `annotation.json` with veracity
(check both `true` and `misinformation` keys — the schema is inconsistent across events, an
artifact of the dataset being built incrementally in 2016 and extended in 2018).

## HumAID (53,531 train / 7,793 dev / 15,160 test)
```bash
curl -sL -o train.parquet "https://huggingface.co/datasets/QCRI/HumAID-all/resolve/refs%2Fconvert%2Fparquet/default/train/0000.parquet"
curl -sL -o validation.parquet "https://huggingface.co/datasets/QCRI/HumAID-all/resolve/refs%2Fconvert%2Fparquet/default/validation/0000.parquet"
curl -sL -o test.parquet "https://huggingface.co/datasets/QCRI/HumAID-all/resolve/refs%2Fconvert%2Fparquet/default/test/0000.parquet"
```
Columns: `tweet_text`, `class_label` (11 humanitarian categories, e.g. `injured_or_dead_people`,
`rescue_volunteering_or_donation_effort`, `sympathy_and_support`).

## IDRISI (215MB — location mention recognition + disambiguation)
```bash
git clone --depth 1 https://github.com/rsuwaileh/IDRISI.git
```
Two subdirectories: `LMR/` (location mention recognition — span extraction) and
`LMD/` (location mention disambiguation — resolving spans to actual geo-coordinates).
This is your direct benchmark for validating the gazetteer/NER geo-resolution module
before trusting it on your own Hindi/regional-language data.

## Still needed (require your credentials — see STATUS.md)
- Reddit (PRAW) — needs OAuth app approval
- Telegram (Telethon) — needs api_id/api_hash from my.telegram.org
- Google Fact Check Tools API — needs a free API key from Google Cloud Console
