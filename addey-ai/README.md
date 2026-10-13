# Addey AI (Addey AI)
Educational assistant for Ethiopian indigenous medicine knowledge. Not a diagnostic tool.

## Run
    python3 scripts/build_data.py   # CSVs in data/ -> src/data.json
    python3 -m http.server 8000     # open the forwarded port 8000

## Structure
- `data/` source CSVs (edit these)
- `scripts/build_data.py` cleans the CSVs and writes `src/data.json`
- `index.html`, `src/style.css`, `src/app.js` the website

## Deploy on Vercel
Static site, no build step. Vercel dashboard > Add New > Project > import this GitHub repo >
Framework Preset "Other", leave build command and output directory empty > Deploy.
Commit `src/data.json` (run `python3 scripts/build_data.py` after any CSV change).
