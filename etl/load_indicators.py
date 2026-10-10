import pandas as pd
import pg8000
from dotenv import load_dotenv
import os

load_dotenv()

conn = pg8000.connect(
    host=os.getenv("DB_HOST"),
    port=int(os.getenv("DB_PORT")),
    database=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD")
)
print("Connected!")

df = pd.read_csv(
    "data/accident_per_10000_per_city.csv",
    sep=";",
    encoding="utf-8-sig",
    skiprows=2
)

df = df.rename(columns={
    "schluessel":      "district_code",
    "regionaleinheit": "district_name",
    "wert":            "value"
})

print("Columns:", list(df.columns))
print("Total rows:", len(df))

cursor = conn.cursor()

cursor.execute("""
    INSERT INTO indicators (code, name, unit, source_system)
    VALUES (%s, %s, %s, %s)
    ON CONFLICT (code) DO NOTHING
""", (
    "accidents_per_10000",
    "Accidents per 10,000 inhabitants",
    "per 10,000 people",
    "fallback_csv"
))
conn.commit()
print("Indicator definition inserted!")

cursor.execute(
    "SELECT indicator_id FROM indicators WHERE code = 'accidents_per_10000'"
)
result = cursor.fetchone()
indicator_id = result[0]
print("Indicator ID:", indicator_id)

inserted = 0

for _, row in df.iterrows():
    state_code = int(str(int(row["district_code"]))[:2])

    cursor.execute("""
        INSERT INTO regions (ags, name, level, state_code)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (ags) DO NOTHING
    """, (
        str(int(row["district_code"])).zfill(8),
        str(row["district_name"]),
        "district",
        state_code
    ))
    conn.commit()

    cursor.execute(
        "SELECT region_id FROM regions WHERE ags = %s",
        (str(int(row["district_code"])).zfill(8),)
    )
    region = cursor.fetchone()
    region_id = region[0]

    cursor.execute("""
        INSERT INTO indicator_values (region_id, indicator_id, year, value)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (region_id, indicator_id, year) DO NOTHING
    """, (
        region_id,
        indicator_id,
        2023,
        float(row["value"])
    ))
    inserted += 1
    if inserted % 50 == 0:
        print(f"Inserted {inserted} rows so far...")

conn.commit()
print(f"Done! Inserted {inserted} indicator values!")

#record import provenance
cursor.execute("""
               INSERT INTO import_runs(source_name, source_url, licence, row_count,
               notes) VALUES(%s, %s, %s, %s, %s)
               """,(
                "accident_per_10000_per_city.csv",
                "https://www.regionalstatistik.de/genesis/online",
                "dl-de/by-2-0",
                inserted,
                "Accident rates per 10,000 inhabitants"
))
conn.commit()
print("Import recorded in import_runs!")

cursor.close()
conn.close()
print("All done!")
