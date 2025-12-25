import sys, json
from geopy.distance import geodesic

output_path = sys.argv[1]

# Dummy data
wells = [{"well": "31/2-12 Y2H", "well_lat": 60.8, "well_lon": 3.5, "rig": "Deepsea Atlantic"}]
rigs = {"Deepsea Atlantic": {"rig_lat": 58.9, "rig_lon": 2.1}}

output = []
for w in wells:
    r = rigs.get(w["rig"])
    dist = geodesic((w["well_lat"], w["well_lon"]), (r["rig_lat"], r["rig_lon"])).km if r else None
    output.append({**w, "rig_lat": r["rig_lat"], "rig_lon": r["rig_lon"], "distance_km": dist})

with open(output_path, "w") as f:
    json.dump(output, f, indent=2)
