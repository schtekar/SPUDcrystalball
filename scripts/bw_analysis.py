import json
import os
from datetime import datetime

BW_DB_PATH = "docs/bw_database.json"
OUT_PATH = "docs/bw_database_summary.json"

if not os.path.exists(BW_DB_PATH):
    print("❌ Fant ikke bw_database.json – avbryter")
    exit(1)

with open(BW_DB_PATH) as f:
    bw_db = json.load(f)

summary = {
    "generated_at": datetime.utcnow().isoformat() + "Z",
    "rig_count": len(bw_db),
    "rigs": []
}

for mmsi, data in bw_db.items():
    summary["rigs"].append({
        "mmsi": mmsi,
        "bw_recent": data.get("bw_recent"),
        "bw_12h": data.get("bw_12h"),
        "bw_1d": data.get("bw_1d"),
        "bw_2d": data.get("bw_2d"),
    })

with open(OUT_PATH, "w") as f:
    json.dump(summary, f, indent=2)

print("✅ BW analyse ferdig → docs/bw_database_summary.json")
