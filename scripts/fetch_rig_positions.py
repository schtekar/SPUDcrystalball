import requests
import json
from datetime import datetime, timedelta
from rig_registry import RIG_MMSI

# --- 1️⃣ Hent brønndata fra GitHub Pages ---
DATA_URL = "https://schtekar.github.io/SPUDcrystalball/data.json"
response = requests.get(DATA_URL)
response.raise_for_status()
wells = response.json()

print(f"Fant {len(wells)} brønner i data.json")

# --- 2️⃣ Finn unike rigger som finnes i rig_registry ---
unique_rigs = {well['rig_name'] for well in wells if well['rig_name'] in RIG_MMSI}
print(f"Unike rigger å hente posisjon for: {unique_rigs}")

# --- 3️⃣ AIS API ---
API_URL = "https://kystdatahuset.no/ws/api/ais/positions/for-mmsis-time"

# Sett tidsintervall siste time
now = datetime.utcnow()
start_time = (now - timedelta(hours=1)).strftime("%Y%m%d%H%M")
end_time = now.strftime("%Y%m%d%H%M")

rig_positions = []

for rig in unique_rigs:
    mmsi = RIG_MMSI[rig]

    payload = {
        "mmsiIds": [mmsi],
        "start": start_time,
        "end": end_time,
        "minSpeed": 0.5
    }

    try:
        r = requests.post(API_URL, json=payload)
        r.raise_for_status()
        data = r.json()
        if data.get("success") and data.get("data") and len(data["data"]) > 0:
            last_pos = data["data"][-1]
            rig_positions.append({
                "rig_name": rig,
                "mmsi": mmsi,
                "lat": last_pos[3],
                "lon": last_pos[2],
                "speed": last_pos[4],
                "course": last_pos[5],
                "timestamp": last_pos[1]
            })
            print(f"{rig}: posisjon lagret")
        else:
            print(f"{rig}: ingen posisjonsdata tilgjengelig i siste time")
    except Exception as e:
        print(f"{rig}: feil ved henting -> {e}")

# --- 4️⃣ Lagre til docs/rig_positions.json ---
with open("docs/rig_positions.json", "w") as f:
    json.dump(rig_positions, f, indent=2)

print(f"✅ Lagret {len(rig_positions)} rigg-posisjoner til docs/rig_positions.json")
