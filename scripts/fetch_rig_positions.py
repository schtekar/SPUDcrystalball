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

# Funksjon for å generere start/end string for timen 23:00-23:59 for N døgn siden
def get_time_interval(days_ago):
    target_date = datetime.utcnow() - timedelta(days=days_ago)
    start = target_date.replace(hour=23, minute=0, second=0, microsecond=0).strftime("%Y%m%d%H%M")
    end = target_date.replace(hour=23, minute=59, second=59, microsecond=0).strftime("%Y%m%d%H%M")
    return start, end

# --- 4️⃣ Hent posisjoner ---
rig_positions = []

for rig in unique_rigs:
    mmsi = RIG_MMSI[rig]
    print(f"\n=== Henter posisjon for {rig} (MMSI {mmsi}) ===")

    for days_ago in [2, 3]:  # 2 og 3 døgn siden
        start_time, end_time = get_time_interval(days_ago)
        payload = {
            "mmsiIds": [mmsi],
            "start": start_time,
            "end": end_time,
            "minSpeed": 0.5
        }

        print(f"\nTidsintervall {days_ago} døgn siden: {start_time} - {end_time}")
        print(f"Payload sendt til API: {payload}")

        try:
            r = requests.post(API_URL, json=payload)
            r.raise_for_status()
            data = r.json()

            print(f"Respons success: {data.get('success')}, data points: {len(data.get('data', []))}")

            if data.get("success") and data.get("data") and len(data["data"]) > 0:
                # Ta siste punkt i timen
                last_pos = data["data"][-1]
                rig_positions.append({
                    "rig_name": rig,
                    "mmsi": mmsi,
                    "days_ago": days_ago,
                    "lat": last_pos[3],
                    "lon": last_pos[2],
                    "speed": last_pos[4],
                    "course": last_pos[5],
                    "timestamp": last_pos[1]
                })
                print(f"{rig} ({days_ago} døgn siden): posisjon lagret")
            else:
                print(f"{rig} ({days_ago} døgn siden): ingen posisjonsdata tilgjengelig")
        except Exception as e:
            print(f"{rig} ({days_ago} døgn siden): feil ved henting -> {e}")

# --- 5️⃣ Lagre til docs/rig_positions.json ---
with open("docs/rig_positions.json", "w") as f:
    json.dump(rig_positions, f, indent=2)

print(f"\n✅ Lagret {len(rig_positions)} rigg-posisjoner til docs/rig_positions.json")
