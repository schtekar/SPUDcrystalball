import pandas as pd

# 1. Last data
url = "https://schtekar.github.io/SPUDcrystalball/data.json"
df = pd.read_json(url)

# 2. Enkel info
print("Totalt antall brønner:", len(df))
print("Formål for brønner (count per type):")
print(df["purpose"].value_counts())

# 3. Brønner med status 'ONLINE/OPERATIONAL'
online = df[df["status"] == "ONLINE/OPERATIONAL"]
print("\nONLINE/OPERATIONAL brønner:", len(online))

# 4. Brønner med blank EntryDate (planlagt)
planned = df[df["entryDate"] == ""]
print("Planlagte brønner:", len(planned))

# 5. Top 5 rigger med flest brønner
print("\nTop 5 rigger:")
print(df.groupby("rig").size().sort_values(ascending=False).head(5))
