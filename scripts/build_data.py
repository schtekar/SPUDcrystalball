import requests
import json
from datetime import datetime, timedelta

# --- Konfig ---
layer = 201  # All wellbores
base_url = "https://factmaps.sodir.no/api/rest/services/Factmaps/FactMapsWGS84/FeatureServer"
query_url = f"{base_url}/{layer}/query"

# Parametre for ArcGIS FeatureServer
params = {
    "where": "1=1",  # Hent alt først, filtrering skjer i Python
    "outFields": "wlbWellboreName,wlbPurpose,wlbStatus,wlbEntryDate,wlbDrillingFacilityFixedOrMove",
    "outSR": 4326,
    "f": "json"
}

# --- Hent data ---
response = requests.get(query_url, params=params)
response.raise_for_status()
data = response.json()

# --- Filtrering ---
today = datetime.today()
cutoff_date = today - timedelta(days=100)
relevant_purposes = {"PRODUCTION", "INJECTION", "WILDCAT"}

filtered_wells = []

for feature in data.get("features", []):
    attr = feature.get("attributes", {})
    geom = feature.get("geometry", {})

    status = (attr.get("wlbStatus") or "").strip()
    entry_date_str = (attr.get("wlbEntryDate") or "").strip()
    purpose = (attr.get("wlbPurpose") or "").strip()

    # Statusfilter
    status_ok = status in {"ONLINE/OPERATIONAL", ""}

    # EntryDate-filter
    if entry_date_str == "":
        entry_ok = True
    else:
        try:
            entry_date = datetime.strptime(entry_date_str[:10], "%Y-%m-%d")
            entry_ok = entry_date >= cutoff_date
        except ValueError:
            entry_ok = False

    # Formål-filter
    purpose_ok = purpose in relevant_purposes

    # Legg til kun hvis alle kriterier er oppfylt og koordinater finnes
    if status_ok and entry_ok and purpose_ok and "x" in geom and "y" in geom:
        filtered_wells.append({
            "well": attr.get("wlbWellboreName"),
            "purpose": purpose,
            "status": status,
            "entryDate": entry_date_str,
            "rig": attr.get("wlbDrillingFacilityFixedOrMove"),
            "lat": geom["y"],
            "lon": geom["x"]
        })

# --- Lagre til JSON ---
with open("docs/data.json", "w") as f:
    json.dump(filtered_wells, f, indent=2)

print(f"Hentet {len(filtered_wells)} relevante brønner")
