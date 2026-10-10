from fastapi import FastAPI
from api.database import get_db


app = FastAPI(
    title="Accident Data API",
    description="German Road Accident Open Data",
    version="1.0.0"
)


# state name to code mapping
STATE_CODES = {
    "SH": 1,  "HH": 2,  "NI": 3,  "HB": 4,
    "NW": 5,  "HE": 6,  "RP": 7,  "BW": 8,
    "BY": 9,  "SL": 10, "BE": 11, "BB": 12,
    "MV": 13, "SN": 14, "ST": 15, "TH": 16
}

# helper function to convert  state name to number


def get_state_code(state: str):
    if state is None:
        return None
    if state.isdigit():
        return int(state)
    return STATE_CODES.get(state.upper())


@app.get("/")
def home():
    return {
        "status": "ok",
        "message": "Accident API is running!",
        "available_states": STATE_CODES
    }


@app.get("/accidents")
def get_accidents(state: str = None, year: str = None):
    conn = get_db()
    cursor = conn.cursor()

    # convert state name to number
    state_num = get_state_code(state)
    if state and state_num is None:
        return {"error": f"unknown state: {state}. Use SN, BE, NW, etc."}

    query = "SELECT COUNT(*) FROM accidents WHERE 1=1"
    params = []

    if state_num:
        query += " AND state_code = %s"
        params.append(state_num)

    if year:
        query += " AND year = %s"
        params.append(int(year))

    cursor.execute(query, params)
    result = cursor.fetchone()

    cursor.close()
    conn.close()

    return {"count": result[0], "state": state,  "state_code": state_num, "year": year}

# earliest and latest year


@app.get("/years")
def get_years(state: str = None):
    conn = get_db()
    cursor = conn.cursor()

    # convert state name to number
    state_num = get_state_code(state)
    if state and state_num is None:
        return {"error": f"unknown state: {state}. Use SN, BE, NW, etc."}

    query = "SELECT MIN(year), MAX(year) FROM accidents WHERE 1=1"
    params = []

    if state_num:
        query += " AND state_code = %s"
        params.append(state_num)

    cursor.execute(query, params)
    result = cursor.fetchone()

    cursor.close()
    conn.close()

    return {
        "earliest_year": result[0],
        "latest_year": result[1],
        "state": state,
        "state_code": state_num
    }

# pedestrian accidents
@app.get("/pedestrian")
def get_pedestrian(state: str = None, year: str = None):
    conn = get_db()
    cursor = conn.cursor()

    # convert state name to number
    state_num = get_state_code(state)
    if state and state_num is None:
        return {"error": f"unknown state: {state}. Use SN, BE, NW, etc."}

    query = "SELECT COUNT(*) FROM accidents WHERE pedestrian = 1"
    params = []

    if state_num:
        query += " AND state_code = %s"
        params.append(state_num)

    if year:
        query += " AND year = %s"
        params.append(int(year))

    cursor.execute(query, params)
    result = cursor.fetchone()

    cursor.close()
    conn.close()

    return {"pedestrian_accidents": result[0], "state": state, "state_code": state_num, "year": year}

# top districts by accidents rate


@app.get("/rates")
def get_rates(top: int = 10):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
                   SELECT r.name, iv.value FROM indicator_values iv
                   JOIN regions r ON r.region_id=iv.region_id
                   ORDER BY iv.value DESC
                   LIMIT %s""", (top,))

    results = cursor.fetchall()

    cursor.close()
    conn.close()

    return {
        "metric": "accidents per 10,000 inhabitants",
        "result": [{"district": row[0], "rate": row[1]} for row in results]
    }

# bicycle accidents
@app.get("/bicycle")
def get_bicycle(state: str = None, year: str = None):
    conn = get_db()
    cursor = conn.cursor()

    # convert state name to number
    state_num = get_state_code(state)
    if state and state_num is None:
        return {"error": f"unknown state: {state}. Use SN, BE, NW, etc."}

    query = "SELECT COUNT(*) FROM accidents WHERE bicycle = 1"
    params = []

    if state_num:
        query += " AND state_code = %s"
        params.append(state_num)

    if year:
        query += " AND year = %s"
        params.append(int(year))

    cursor.execute(query, params)
    result = cursor.fetchone()

    cursor.close()
    conn.close()

    return {"bicycle_accidents": result[0], "state": state, "state_code": state_num, "year": year}

#metadata
@app.get("/metadata")
def get_metadata():
    return {
        "sources" :[
            {
                "name": "accident_per_location_2023.csv",
                "url": "https://www.opengeodata.nrw.de/produkte/transport_verkehr/unfallatlas/",
                "licence": "dl-de/by-2-0",
                "format": "CSV",
                "rows": 269048
            },
            {
                "name": "accident_per_location_2021_in_Schleswig-Holstein.csv",
                "url": "https://www.opengeodata.nrw.de/produkte/transport_verkehr/unfallatlas/",
                "licence": "dl-de/by-2-0",
                "format": "CSV",
                "rows": 9790
            },
            {
                "name": "accident_per_10000_per_city.csv",
                "url": "https://www.opengeodata.nrw.de/produkte/transport_verkehr/unfallatlas/",
                "licence": "dl-de/by-2-0",
                "format": "CSV",
                "rows": 400
            }
        ]
    }
            