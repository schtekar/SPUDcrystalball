import pandas as pd
import json

url = "https://schtekar.github.io/SPUDcrystalball/data.json"
df = pd.read_json(url)

summary = {
    "total_wells": len(df),
    "purpose_counts": df["purpose"].value_counts().to_dict(),
    "online_operational": len(df[df["status"] == "ONLINE/OPERATIONAL"]),
    "planned": len(df[df["entryDate"] == ""]),
    "top_rigs": df.groupby("rig").size().sort_values(ascending=False).head(5).to_dict()
}

# Skriv summary til fil
with open("docs/analysis_summary.json", "w") as f:
    json.dump(summary, f, indent=2)
