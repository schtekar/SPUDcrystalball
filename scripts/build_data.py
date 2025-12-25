import json
from geopy.distance import geodesic

# ---------- DUMMY DATA ----------

wells = [
    {"well": "31/2-12 Y2H", "well_lat": 60.8, "well_lon": 3.5, "rig": "Deepsea Atlantic"}
]

rigs = {
    "Deepsea Atlantic": {"rig_lat": 58.9, "rig_lon": 2.1}
}

# ---------- KOBLING ----------

output = []
for w in wells:
    r = rigs.get(w["rig"])
    if r:
        dist = geodesic((w["well_lat"], w["well_lon"]), (r["rig_lat"], r["rig_lon"])).km
    else:
        dist = None

    output.append({
        **w,
        "rig_lat": r["rig_lat"] if r else None,
        "rig_lon": r["rig_lon"] if r else None,
        "distance_km": dist
    })

# ---------- SKRIV JSON ----------

with open("docs/data.json", "w") as f:
    json.dump(output, f, indent=2)
