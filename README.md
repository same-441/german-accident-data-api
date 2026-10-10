# German Road Accident Data API

A Python data service that merges three official German open-data sources on road accidents into one PostgreSQL database and exposes it through a documented REST API built with FastAPI.

Built as a university project for *Database and Web Technologies* (M.Sc. Automotive Software Engineering, TU Chemnitz, June 2026).

## Highlights

- **ETL pipeline** in Python (pandas, pg8000) that cleans and loads **278,838 accident records** and **400 regional indicators**
- **Unified 5-table PostgreSQL schema** with keys, constraints and an index for fast filtering by state and year
- **Duplicate-safe imports** using unique source IDs and `ON CONFLICT DO NOTHING`
- **Data provenance**: every import run is logged with source, URL, licence and row count
- **REST API** with 7 endpoints and interactive Swagger documentation

## How it works

```
Unfallatlas CSV (Germany 2023) ─┐
Unfallatlas CSV (Schleswig-     ├─► ETL (pandas: clean, rename, convert) ─► PostgreSQL ─► FastAPI ─► JSON / Swagger UI
  Holstein 2021)                │
Regionalstatistik CSV (rates) ──┘
```

The source files use different layouts: semicolon separators, German decimal commas in coordinates and extra header rows. The ETL scripts normalise them into one consistent schema.

## Tech stack

Python 3.11 · FastAPI · Uvicorn · pandas · pg8000 · PostgreSQL · python-dotenv

## Database schema

| Table | Purpose |
| --- | --- |
| `accidents` | One row per accident: time, type, participants (bicycle, car, pedestrian, motorcycle), coordinates, region codes |
| `regions` | Districts with their official key (AGS) and state |
| `indicators` | Definitions of regional statistics, e.g. accidents per 10,000 inhabitants |
| `indicator_values` | Indicator value per region and year |
| `import_runs` | Log of every import: source, URL, licence, row count, timestamp |

Full definition: [`sql/schema.sql`](sql/schema.sql)

## API endpoints

| Endpoint | Description | Example |
| --- | --- | --- |
| `GET /accidents` | Number of accidents, filtered by state and year | `/accidents?state=SN&year=2023` |
| `GET /years` | Earliest and latest year with data, optionally per state | `/years?state=NW` |
| `GET /pedestrian` | Accidents involving pedestrians | `/pedestrian?state=BE&year=2023` |
| `GET /bicycle` | Accidents involving bicycles | `/bicycle?state=SN&year=2023` |
| `GET /rates` | Districts with the highest accident rate per 10,000 inhabitants | `/rates?top=5` |
| `GET /metadata` | Data sources, licences and row counts | `/metadata` |
| `GET /` | Health check and list of state codes | `/` |

States can be passed as abbreviations (`SN`, `BE`, `NW`, …) or numeric codes (`14`, `11`, `5`, …).

## Getting started

**1. Install dependencies** (Python 3.11+)

```bash
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS / Linux
pip install -r requirements.txt
```

**2. Create the database**

Create a PostgreSQL database named `accidents_db`, then run the schema:

```bash
psql -U postgres -d accidents_db -f sql/schema.sql
```

**3. Configure the connection**

Copy `.env.example` to `.env` and enter your database password.

**4. Download the data**

Download the CSV files from the sources below and place them in a `data/` folder:

- `accident_per_location_2023.csv`
- `accident_per_location_2021_in_Schleswig-Holstein.csv`
- `accident_per_10000_per_city.csv`

**5. Load the data**

```bash
python etl/load_accidents.py
python etl/load_indicators.py
```

**6. Start the API** (from the project root)

```bash
uvicorn api.main:app --reload
```

Open **http://localhost:8000/docs** for the interactive API documentation.

## Project structure

```
├── api/
│   ├── main.py            # FastAPI app and endpoints
│   └── database.py        # PostgreSQL connection
├── etl/
│   ├── load_accidents.py  # Loads Unfallatlas accident records
│   └── load_indicators.py # Loads regions and accident rates
├── sql/
│   └── schema.sql         # Database schema
├── .env.example
└── requirements.txt
```

## Data sources

| Source | Content | Licence |
| --- | --- | --- |
| [Unfallatlas](https://www.opengeodata.nrw.de/produkte/transport_verkehr/unfallatlas/) | Accidents with personal injury, 2023 (Germany) and 2021 (Schleswig-Holstein) | dl-de/by-2-0 |
| [Regionalstatistik](https://www.regionalstatistik.de/genesis/online) | Accidents per 10,000 inhabitants by district | dl-de/by-2-0 |

The data files are not included in this repository because of their size.

## Author

**Sammer** – M.Sc. Automotive Software Engineering, TU Chemnitz
