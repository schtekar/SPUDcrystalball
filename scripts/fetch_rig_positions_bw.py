"""
fetch_rig_positions_bw.py

Henter AIS-posisjoner fra BarentsWatch Live AIS API
Filtrerer på rigg-MMSI
"""

import os
import requests
from datetime import datetime, timedelta, timezone
import json

from rig_registry import RIG_MMSI

TOKEN_URL = "https://id.barentswatch.no/connect/token"
AIS_URL = "https://live.ais.barentswatch.no/live/v1/latest/ais"

CLIENT_ID = os.getenv("BWAPI_CLIENTID_URLENCODED")
CLIENT_SECRET = os.getenv("BWAPI_PWSECRET")

OUT_PATH = "docs/rig_positions_bw.json"

if not CLIENT_ID or not CLIENT_SECRET:
    raise RuntimeError("❌ Mangler BWAPI secrets")

# -----------------------------
# 1. Hent access token
# -----------------------------
token_resp = requests.post(
    TOKEN_URL,
    headers={"Content-Type": "application/x-www-form-urlencoded"},
    data={
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "scope": "ais",
    },
    timeout=30,
)

token_resp.raise_for_status()
access_token = token_resp.json()["access_token"]

# -----------------------------
# 2. Hent AIS-data (siste X min)
# -----------------------------
since_time = (
    datetime.now(timezone.utc) - timedelta(minutes=10)
).strftime("%Y-%m-%dT%H:%M:%SZ")

resp = requests.get(
    AIS_URL,
    headers={
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json",
    },
    params={"since": since_time},
    timeout=60,
)

resp.raise_for_status()
messages = resp.json()

print(f"📡 Mottok {len(messages)} AIS-meldinger")

# -----------------------------
# 3. Filtrer på rigg-MMSI
# -----------------------------
rig_mmsi_set = set(RIG_MMSI.values())

latest_by_mmsi = {}

for msg in messages:
    mmsi = msg.get("mmsi")
    lat = msg.get("latitude")
    lon = msg.get("longitude")
    msgtime = msg.get("msgtime")

    if (
        mmsi in rig_mmsi_set
        and lat not in (None, 0)
        and lon not in (None, 0)
    ):
        latest_by_mmsi[mmsi] = {
            "mmsi": mmsi,
            "latitude": lat,
            "longitude": lon,
            "msgtime": msgtime,
            "source": "barentswatch",
        }

print(f"🛢️ Fant {len(latest_by_mmsi)} rigger med gyldig posisjon")

# -----------------------------
# 4. Skriv til fil
# -----------------------------
with open(OUT_PATH, "w") as f:
    json.dump(list(latest_by_mmsi.values()), f, indent=2)

print(f"✅ Lagret {OUT_PATH}")
