import requests
import json
from datetime import datetime, timedelta
import os
from rig_registry import RIG_MMSI

# --------------------
# KONFIG
# --------------------
AUTH_URL = "https://kystdatahuset.no/ws/api/auth/login"
AIS_URL = "https://kystdatahuset.no/ws/api/ais/positions/for-mmsis-time"

USERNAME = os.getenv("KYSTDATAHUSET_USERNAME")
PASSWORD = os.getenv("KYSTDATAHUSET_PASSWORD")

if not USERNAME or not PASSWORD:
    raise RuntimeError("❌ Mangler KYSTDATAHUSET_USERNAME eller PASSWORD i environment")

# --------------------
# 1️⃣ AUTENTISERING
# --------------------
print("🔐 Autentiserer mot Kystdatahuset...")

auth_payload = {
    "username": USERNAME,
    "password": PASSWORD
}

auth_headers = {
    "Content-Type": "application/json",
    "Accept": "*/*",
    "User-Agent": "SPUDcrystalball/1.0"
}

auth_resp = requests.post(AUTH_URL, json=auth_payload, headers=auth_headers)
auth_resp.raise_for_status()
auth_data = auth_resp.json()

if not auth_data.get("success"):
    raise RuntimeError(f"❌ Autentisering feilet: {auth_data}")

JWT = auth_data["data"]["JWT"]
print("✅ Autentisering OK – JWT mottatt")

# --------------------
# 2️⃣ HENT BRØNNDATA
# --------------------
DATA_URL = "https://schtekar.github.io/SPUDcrystalball/data.json"
wells = requests.get(DATA_URL).json()

unique_rigs = {w["rig_name"] for w in wells if w["rig_name"] in RIG_MMSI}
print(f"🎯 Rigger funnet i registry: {unique_rigs}")

# --------------------
# 3️⃣ TIDSINTERVALL
# --------------------
def get_time_interval(days_ago):
    d = datetime.utcnow() - timedelta(days=days_ago)
    start = d.replace(hour=23, minute=0, second=0).strftime("%Y%m%d%H%M")
    end = d.replace(hour=23, minute=59, second=59).strftime("%Y%m%d%H%M")
    return start, end

# --------------------
# 4️⃣ HENT POSISJONER
# --------------------
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {JWT}",
    "User-Agent": "SPUDcrystalball/1.0"
}

rig_positions = []

for rig in unique_rigs:
    mmsi = RIG_MMSI[rig]
    print(f"\n🚢 {rig} (MMSI {mmsi})")

    for days_ago in [2, 3]:
        start, end = get_time_interval(days_ago)
        payload = {
            "mmsiIds": [mmsi],
            "start": start,
            "end": end,
            "minSpeed": 0
        }

        print(f"  ⏱ {days_ago} døgn siden: {start}–{end}")

        r = requests.post(AIS_URL, json=payload, headers=headers)
        r.raise_for_status()
        data = r.json()

        print(f"    → success={data.get('success')} datapunkter={len(data.get('data', []))}")

        if data.get("success") and data.get("data"):
            last = data["data"][-1]
            rig_positions.append({
                "rig_name": rig,
                "mmsi": mmsi,
                "days_ago": days_ago,
                "lat": last[3],
                "lon": last[2],
                "speed": last[4],
                "course": last[5],
                "timestamp": last[1]
            })

# --------------------
# 5️⃣ LAGRE RESULTAT
# --------------------
with open("docs/rig_positions.json", "w") as f:
    json.dump(rig_positions, f, indent=2)

print(f"\n✅ Lagret {len(rig_positions)} posisjoner til docs/rig_positions.json")
