"""Build src/data.json from the CSV files in data/.  Run: python3 scripts/build_data.py"""
import json, re
import pandas as pd

def read(name):
    for enc in ("utf-8", "utf-8-sig", "cp1252"):
        try:
            return pd.read_csv(f"data/{name}", encoding=enc)
        except UnicodeDecodeError:
            pass
    raise SystemExit(f"Cannot decode {name}")

cl = lambda x: re.sub(r"\s+", " ", str(x)).strip()

def level(t):
    m = re.search(r"(High|Medium|Low)", t, re.I)
    return m.group(1).capitalize() if m else "Unknown"

def reason(t):
    parts = re.split(r"Reason\s*:?", t, maxsplit=1)
    return cl(parts[1]) if len(parts) > 1 else ""

def local_name(t):
    t = re.sub(r"\?+", "", cl(t))          # Amharic script was lost as '?' in the CSV
    t = re.sub(r"\(\s*\)", "", t).strip(" -")
    return re.sub(r"\(([^)]*)\)", r"\1", t).strip() if t.startswith("(") else t

disease, symptom, plant, ref = (read(n) for n in
    ("DISEASE.csv", "SYMPTOM.csv", "PLANT.csv", "REFERENCE.csv"))

D = [dict(id=r.Disease_ID, name=cl(r.Disease_name), cat=cl(r.Category), lvl=level(cl(r.Severity)),
          why=reason(str(r.Severity)), desc=cl(r.Description), cause=cl(r.Cause), risk=cl(r.Risk_factors))
     for r in disease.itertuples()]
S = [dict(d=r.Disease_ID, n=cl(r.symptom_name), sev=cl(r.severity), c=cl(r.common_level))
     for r in symptom.itertuples()]

refs, plant_ref = {}, {}
for r in ref.drop_duplicates(["disease_Id", "international_link"]).itertuples():
    item = [cl(r.internatiional_Source_Name), r.international_link]
    if str(r.disease_Id).startswith("D0"):
        refs.setdefault(r.disease_Id, []).append(item)
    else:
        plant_ref[str(r.disease_Id).replace("TUB_", "TB_")] = item   # TUB_ vs TB_ ID mismatch

P = []
for r in plant.itertuples():
    name = cl(r.Plant_Name)
    if name.lower().startswith("traditional use only"):   # MAL_P003 had a warning in the name field
        name = "Broad-leaved Croton"
    P.append(dict(id=r.Plant_ID, d=r.deases_name, name=name, sci=cl(r.scientific_name), fam=cl(r.plant_familiy),
                  loc=local_name(r.Local_name), part=cl(r.part_used).capitalize(), prep=cl(r.Preparation),
                  use=cl(r.traditional_use), ev=cl(r.evidence_level), reg=cl(r.region_in_ethiopia),
                  warn=cl(r.safety_warning), ref=plant_ref.get(r.Plant_ID)))

with open("src/data.json", "w", encoding="utf-8") as f:
    json.dump(dict(d=D, s=S, p=P, r=refs), f, ensure_ascii=False, separators=(",", ":"))
print(f"data.json: {len(D)} diseases, {len(S)} symptoms, {len(P)} plants")
