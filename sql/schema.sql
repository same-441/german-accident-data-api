-- German road accident open data: unified schema (PostgreSQL)

CREATE TABLE regions (
    region_id   SERIAL PRIMARY KEY,
    ags         VARCHAR(8)   UNIQUE NOT NULL,   -- official municipality/district key
    name        VARCHAR(255) NOT NULL,
    level       VARCHAR(20)  NOT NULL,
    population  INTEGER,
    state_code  SMALLINT
);

CREATE TABLE accidents (
    accident_id    SERIAL PRIMARY KEY,
    uid            VARCHAR(30) UNIQUE,          -- source ID, prevents duplicate imports
    year           SMALLINT NOT NULL,
    month          SMALLINT,
    hour           SMALLINT,
    weekday        SMALLINT,
    category       SMALLINT,
    accident_type  SMALLINT,
    bicycle        SMALLINT,
    car            SMALLINT,
    pedestrian     SMALLINT,
    motorcycle     SMALLINT,
    lon            NUMERIC(14,10),
    lat            NUMERIC(14,10),
    state_code     SMALLINT,
    district_code  SMALLINT,
    municipality   SMALLINT
);

CREATE INDEX idx_accidents_state_year ON accidents (state_code, year);

CREATE TABLE indicators (
    indicator_id   SERIAL PRIMARY KEY,
    code           VARCHAR(50)  UNIQUE NOT NULL,
    name           VARCHAR(255) NOT NULL,
    unit           VARCHAR(50),
    source_system  VARCHAR(100)
);

CREATE TABLE indicator_values (
    id            SERIAL PRIMARY KEY,
    region_id     INTEGER NOT NULL REFERENCES regions (region_id),
    indicator_id  INTEGER NOT NULL REFERENCES indicators (indicator_id),
    year          SMALLINT NOT NULL,
    value         NUMERIC(12,4),
    UNIQUE (region_id, indicator_id, year)
);

CREATE TABLE import_runs (
    run_id       SERIAL PRIMARY KEY,
    source_name  VARCHAR(100),
    source_url   TEXT,
    licence      VARCHAR(100),
    imported_at  TIMESTAMP DEFAULT NOW(),
    row_count    INTEGER,
    notes        TEXT
);
