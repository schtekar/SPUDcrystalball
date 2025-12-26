import pandas as pd
import json
import os

DATA_PATH = "docs/data.json"
OUT_PATH = "docs/analysis_summary.json"

# --- 1️⃣ Last data ---
if not os.path.exists(DATA_PATH):
    print(f"❌ Fant ikke {DATA_PATH}. Avbryter analyse.")
    exit(1)

df = pd.read_json(DATA_PATH)

print("Kolonner i datasettet:")
print(df.columns.tolist())
print("Antall rader:", len(df))

# --- 2️⃣ Sørg for at nødvendige kolonner finnes ---
expected_cols = [
    "purpose",
    "status",
    "entryDate",
    "rig_name",
    "rig_type",
    "operator",
    "well_type",
    "field"
]

for col in expected_cols:
    if col not in df.columns:
        df[col] = "UNKNOWN"

# Normaliser tekst (case-insensitive analyser)
df["purpose"] = df["purpose"].astype(str).str.upper()
df["status"] = df["status"].astype(str).str.upper()

# --- 3️⃣ Analyse ---
summary = {
    "total_wells": int(len(df)),

    "purpose_counts": df["purpose"].value_counts().to_dict(),

    "status_counts": df["status"].value_counts().to_dict(),

    "planned_wells": int((df["entryDate"] == "").sum()),

    "online_operational": int((df["status"] == "ONLINE/OPERATIONAL").sum()),

    "top_rigs": (
        df[df["rig_name"] != "UNKNOWN"]
        .groupby("rig_name")
        .size()
        .sort_values(ascending=False)
        .head(5)
        .to_dict()
    ),

    "rig_type_counts": df["rig_type"].value_counts().to_dict(),

    "top_operators": (
        df[df["operator"] != "UNKNOWN"]
        .groupby("operator")
        .size()
        .sort_values(ascending=False)
        .head(5)
        .to_dict()
    ),

    "well_type_counts": df["well_type"].value_counts().to_dict(),

    "field_counts": (
        df[df["field"] != "UNKNOWN"]
        .groupby("field")
        .size()
        .sort_values(ascending=False)
        .head(10)
        .to_dict()
    )
}

# --- 4️⃣ Lagre ---
with open(OUT_PATH, "w") as f:
    json.dump(summary, f, indent=2)

print(f"✅ Analyse fullført. Lagret til {OUT_PATH}")
