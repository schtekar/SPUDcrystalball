import pandas as pd
import json
import os

url = "docs/data.json"  # Lokalt fil

if not os.path.exists(url):
    print(f"Feil: {url} finnes ikke. Avbryter analysen.")
    exit(1)

df = pd.read_json(url)

# Sørg for at nødvendige kolonner finnes
for col in ["rig_name", "rig_type", "purpose", "status", "entryDate"]:
    if col not in df.columns:
        df[col] = "UNKNOWN"

summary = {
    "total_wells": len(df),
    "purpose_counts": df["purpose"].value_counts().to_dict(),
    "online_operational": len(df[df["status"] == "ONLINE/OPERATIONAL"]),
    "planned": len(df[df["entryDate"] == ""]),
    "top_rigs": df.groupby("rig_name").size().sort_values(ascending=False).head(5).to_dict(),
    "rig_type_counts": df["rig_type"].value_counts().to_dict()
}

# Skriv summary til fil
with open("docs/analysis_summary.json", "w") as f:
    json.dump(summary, f, indent=2)

print("✅ Analyse fullført. Resultat lagret i docs/analysis_summary.json")
