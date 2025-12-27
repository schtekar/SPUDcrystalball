"""
bw_merge.py

Håndterer BarentsWatch AIS data og lager historiske snapshots per rigg.

Struktur:
{
    "rig_mmsi": {
        "bw_database": [..løpende meldinger..],
        "bw_recent": {...nyeste melding},
        "bw_12h": {...melding ~12h gammel},
        "bw_1d": {...melding fra 1d},
        "bw_2d": {...melding fra 2d}
    }
}
"""

import os
import json
from datetime import datetime, timezone, timedelta

# -----------------------------
# Konfig
# -----------------------------
BW_POSITIONS_PATH = "docs/rig_positions_bw.json"
BW_DATABASE_PATH = "docs/bw_database.json"
MAX_RUNNING = 12  # maks meldinger i bw_database per rigg
BW_12H_AGE = timedelta(hours=12)

# -----------------------------
# Hjelpefunksjoner
# -----------------------------
def load_json(path, default=None):
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return default if default is not None else {}

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

def parse_iso(dt_str):
    try:
        return datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
    except Exception:
        return None

# -----------------------------
# 1. Last inn BW-posisjoner
# -----------------------------
bw_positions = load_json(BW_POSITIONS_PATH, [])

if not bw_positions:
    print("⚠️ Ingen BW-posisjoner funnet. Avslutter.")
    exit(0)

# -----------------------------
# 2. Last inn eksisterende bw_database
# -----------------------------
bw_db = load_json(BW_DATABASE_PATH, {})

now = datetime.now(timezone.utc)

# -----------------------------
# 3. Oppdater bw_database med nye meldinger
# -----------------------------
for msg in bw_positions:
    mmsi = str(msg["mmsi"])
    msgtime = parse_iso(msg["msgtime"])
    if msgtime is None:
        continue

    # Init rigg i db hvis ikke eksisterer
    if mmsi not in bw_db:
        bw_db[mmsi] = {
            "bw_database": [],
            "bw_recent": None,
            "bw_12h": None,
            "bw_1d": None,
            "bw_2d": None
        }

    # Legg til i løpende database
    bw_db[mmsi]["bw_database"].append(msg)
    # Sorter etter timestamp, behold maks MAX_RUNNING meldinger
    bw_db[mmsi]["bw_database"].sort(key=lambda x: parse_iso(x["msgtime"]))
    bw_db[mmsi]["bw_database"] = bw_db[mmsi]["bw_database"][-MAX_RUNNING:]

# -----------------------------
# 4. Oppdater snapshots
# -----------------------------
for mmsi, rig_data in bw_db.items():
    db_msgs = rig_data["bw_database"]
    if not db_msgs:
        continue

    # Nyeste melding
    latest_msg = max(db_msgs, key=lambda x: parse_iso(x["msgtime"]))
    rig_data["bw_recent"] = latest_msg

    # Oppdater bw_12h hvis noen melding har nådd ~12h
    if rig_data["bw_12h"] is None:
        # Finn melding som er minst 12h gammel
        twelve_hour_msg = None
        for m in db_msgs:
            m_time = parse_iso(m["msgtime"])
            if m_time and (now - m_time) >= BW_12H_AGE:
                twelve_hour_msg = m
        if twelve_hour_msg:
            rig_data["bw_12h"] = twelve_hour_msg

# -----------------------------
# 5. Daglig snapshot (kjør f.eks. kl 0:00)
# -----------------------------
# bw_1d <- bw_12h, bw_2d <- bw_1d
for mmsi, rig_data in bw_db.items():
    if rig_data["bw_12h"] is not None:
        rig_data["bw_2d"] = rig_data.get("bw_1d")  # gamle 1d blir 2d
        rig_data["bw_1d"] = rig_data.get("bw_12h") # 12h blir 1d snapshot

# -----------------------------
# 6. Skriv tilbake til disk
# -----------------------------
save_json(BW_DATABASE_PATH, bw_db)

print(f"✅ Oppdatert BW database med {len(bw_positions)} nye meldinger og {len(bw_db)} rigger.")
