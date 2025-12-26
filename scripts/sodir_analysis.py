import pandas as pd
import json

url = "https://schtekar.github.io/SPUDcrystalball/data.json"
df = pd.read_json(url)

# Sikre at kolonner finnes
if "rig_name" not in df.columns:
    df["rig_name"] = "UNKNOWN"
if "rig_type" not in df.columns:
    df["rig_type"] = "UNKNOWN"

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
