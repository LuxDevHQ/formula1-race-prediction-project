CREATE TABLE IF NOT EXISTS drivers (
    driver_id TEXT PRIMARY KEY,
    code TEXT,
    given_name TEXT NOT NULL,
    family_name TEXT NOT NULL,
    nationality TEXT
);

CREATE TABLE IF NOT EXISTS constructors (
    constructor_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    nationality TEXT
);

CREATE TABLE IF NOT EXISTS races (
    race_id SERIAL PRIMARY KEY,
    season INT NOT NULL,
    round INT NOT NULL,
    race_name TEXT NOT NULL,
    circuit_id TEXT,
    race_date DATE,
    UNIQUE (season, round)
);

CREATE TABLE IF NOT EXISTS results (
    result_id SERIAL PRIMARY KEY,
    race_id INT NOT NULL REFERENCES races(race_id),
    driver_id TEXT NOT NULL REFERENCES drivers(driver_id),
    constructor_id TEXT NOT NULL REFERENCES constructors(constructor_id),
    grid INT,
    finish_position INT,
    points NUMERIC,
    status TEXT,
    UNIQUE (race_id, driver_id)
);

CREATE TABLE IF NOT EXISTS lap_times (
    lap_time_id SERIAL PRIMARY KEY,
    race_id INT NOT NULL REFERENCES races(race_id),
    driver_id TEXT NOT NULL REFERENCES drivers(driver_id),
    lap_number INT NOT NULL,
    lap_time_ms INT,
    sector1_ms INT,
    sector2_ms INT,
    sector3_ms INT,
    UNIQUE (race_id, driver_id, lap_number)
);

CREATE TABLE IF NOT EXISTS telemetry (
    telemetry_id BIGSERIAL PRIMARY KEY,
    race_id INT NOT NULL REFERENCES races(race_id),
    driver_id TEXT NOT NULL REFERENCES drivers(driver_id),
    sample_ts TIMESTAMPTZ NOT NULL,
    speed NUMERIC,
    throttle NUMERIC,
    brake NUMERIC,
    drs INT,
    gear INT,
    rpm INT
);
