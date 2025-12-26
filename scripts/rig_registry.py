"""
rig_registry.py

- Én sann kilde for rigg → MMSI
- Hjelpefunksjoner for oppslag
"""

# -----------------------------
# Rigg → MMSI register
# -----------------------------

RIG_MMSI = {
    "MÆRSK GUARDIAN": 577494000,
    "WEST LINUS": 257095000,
    "LINUS": 257095000,  # alias
    "WEST ELARA": 259783000,
    "WEST EPSILON": 351635000,
    "NOBLE INTEGRATOR": 538010630,  # samme rigg, nytt navn
    "VALARIS VIKING": 538004075,
    "SCARABEO 8": 308928000,
    "DEEPSEA ABERDEEN": 310713000,
    "ASKEPOTT": 257459000,
    "TRANSOCEAN ENDURANCE": 538010768,
    "COSLPROMOTER": 565798000,
    "TRANSOCEAN EQUINOX": 538010767,
    "COSLINNOVATOR": 566391000,
    "DEEPSEA NORDKAPP": 310776000,
    "NOBLE INVINCIBLE": 538010632,
    "TRANSOCEAN ENABLER": 258615000,
    "DEEPSEA YANTAI": 311000483,
    "SHELF DRILLING BARSK": 636016111,
    "ASKELADDEN": 257452000,
    "COSLPIONEER": 563050900,
    "TRANSOCEAN SPITSBERGEN": 538004905,
    "COSLPROSPECTOR": 565369000,
    "DEEPSEA STAVANGER": 310767000,
    "TRANSOCEAN ENCOURAGE": 258627000,
    "DEEPSEA ATLANTIC": 310766000,
    "DEEPSEA BOLLSTA": 257440000,
}


# -----------------------------
# Hjelpefunksjoner
# -----------------------------

def normalize_rig_name(name: str) -> str:
    """
    Normaliserer riggnavn for oppslag
    """
    if not name:
        return ""
    return name.strip().upper()


def get_mmsi_for_rig(rig_name: str) -> int | None:
    """
    Returnerer MMSI for rigg, eller None hvis ukjent
    """
    key = normalize_rig_name(rig_name)
    return RIG_MMSI.get(key)


def list_known_rigs() -> list[str]:
    """
    Returnerer sortert liste over alle kjente rigger
    """
    return sorted(RIG_MMSI.keys())
