import pg8000
from dotenv import load_dotenv
import os
import pandas as pd

load_dotenv()

conn = pg8000.connect(
    host=os.getenv("DB_HOST"),
    port=int(os.getenv("DB_PORT")),
    database=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
)
print("Connected to Database Successfully!")

cursor = conn.cursor()

csv_files = [
    "data/accident_per_location_2023.csv",
    "data/accident_per_location_2021_in_Schleswig-Holstein.csv",
]

for file in csv_files:
    print(f"\nLoading: {file}")
    df = pd.read_csv(
        file,
        sep=";",
        encoding="utf-8-sig",
        low_memory=False
    )
    df = df.rename(columns={
        "UIDENTSTLAE": "uid",
        "UJAHR": "year",
        "UMONAT": "month",
        "USTUNDE": "hour",
        "UWOCHENTAG": "weekday",
        "UKATEGORIE": "category",
        "UART": "accident_type",
        "IstRad": "bicycle",
        "IstPKW": "car",
        "IstFuss": "pedestrian",
        "IstKrad": "motorcycle",
        "XGCSWGS84": "lon",
        "YGCSWGS84": "lat",
        "ULAND": "state_code",
        "UKREIS": "district_code",
        "UGEMEINDE": "municipality"
    })
    df["lon"] = df["lon"].astype(str).str.replace(",", ".").astype(float)
    df["lat"] = df["lat"].astype(str).str.replace(",", ".").astype(float)

    df = df[["uid", "year", "month", "hour", "weekday", "category", "accident_type", "bicycle",
            "car", "pedestrian", "motorcycle", "lon", "lat", "state_code",
             "district_code", "municipality"]]
    print("Total rows:", len(df))

    inserted = 0
    for _, row in df.iterrows():
        cursor.execute("""
            INSERT INTO accidents(uid, year, month, hour , weekday, category, accident_type,
                       bicycle, car, pedestrian, motorcycle, lon, lat, state_code,district_code,
                       municipality
                       )Values(
                       %s, %s, %s, %s, %s,
                       %s, %s, %s, %s,
                       %s, %s, %s, %s,
                       %s, %s, %s
                       )
                       ON CONFLICT (uid) DO NOTHING
                       """, (
            str(row["uid"]),
            int(row["year"]),
            int(row["month"]),
            int(row["hour"]),
            int(row["weekday"]),
            int(row["category"]),
            int(row["accident_type"]),
            int(row["bicycle"]),
            int(row["car"]),
            int(row["pedestrian"]),
            int(row["motorcycle"]),
            float(row["lon"]),
            float(row["lat"]),
            int(row["state_code"]),
            int(row["district_code"]),
            int(row["municipality"]),
        ))
        inserted += 1
        if inserted % 10000 == 0:
            print(f" Finished: {inserted} rows so far....")
    conn.commit()
    print(f" Finished: {inserted} rows inserted from {file}")

    cursor.execute("""
        INSERT INTO import_runs (source_name, source_url, licence, row_count, notes)
        VALUES (%s, %s, %s, %s, %s)
    """, (
        file,
        "https://www.opengeodata.nrw.de/produkte/transport_verkehr/unfallatlas/",
        "dl-de/by-2-0",
        inserted,
        "Loaded from fallback ZIP"
    ))
    conn.commit()
    print(f"  Import recorded for {file}")

cursor.close()
conn.close()
print("\nAll files loaded successfully!")
