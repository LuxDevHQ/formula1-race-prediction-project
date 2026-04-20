# Analyzing and Predicting Formula 1 (F1) Race Results – 2026 Season

A production-style Data Science + Data Engineering portfolio project that integrates **Ergast API**, **OpenF1 API**, and **FastF1** to build a full pipeline from ingestion to model deployment.

---

## 1) Project Overview

### Problem Statement
Formula 1 outcomes are influenced by driver skill, constructor performance, track characteristics, weather, and race strategy. Students often build only dashboards or small notebooks, but hiring teams look for end-to-end projects that include ingestion, storage, feature pipelines, machine learning, and deployment.

### Why This Project Matters
This project mirrors real analytics workflows used in sports analytics, betting intelligence, media analytics, and race strategy prototyping:
- Build robust data pipelines from multiple APIs
- Model race outcomes with proper supervised learning
- Deploy reproducible prediction workflows for decision support

### Objectives
1. Build a multi-source F1 data platform for seasons 2021–2025 (minimum historical baseline) and 2026 race-week updates.
2. Engineer race-level and driver-level features suitable for supervised learning.
3. Train and compare classification models for **Top-3 finish** and **race winner** prediction.
4. Predict **points scored** as an auxiliary target.
5. Serve insights and predictions in a Streamlit app.

### Data Sources and How They Complement Each Other
- **Ergast API (Historical Baseline):** race schedules, results, qualifying, lap times for multi-season history.
- **OpenF1 API (Live / Telemetry):** real-time sessions, telemetry, lap-level pace indicators, and event timing.
- **FastF1 (Python Session Interface):** convenient and structured access to session-level timing/track-status data with caching.

**Integration logic:** Ergast provides broad historical consistency; FastF1 adds structured session detail; OpenF1 adds near real-time telemetry features for race-week updates.

---

## 2) Architecture Diagram (Markdown)

```text
                  ┌───────────────────────┐
                  │   Ergast API (REST)   │
                  └───────────┬───────────┘
                              │
                  ┌───────────▼───────────┐
                  │ OpenF1 API (REST/live)│
                  └───────────┬───────────┘
                              │
                  ┌───────────▼───────────┐
                  │ FastF1 (Python client)│
                  └───────────┬───────────┘
                              │
                    src/ingestion/*.py
                              │
                              ▼
                    data/raw/*.csv|parquet
                              │
                    src/processing/clean_data.py
                              │
                              ▼
                    data/processed/model_table.parquet
                              │
                    src/features/build_features.py
                              │
                              ▼
                    src/models/train.py + evaluate.py
                              │
                              ▼
                  artifacts/*.pkl + metrics/*.json
                              │
                              ▼
                        app/streamlit_app.py
```

---

## 3) End-to-End Pipeline

1. **Data ingestion:** pull historical races/qualifying/laps from Ergast, session+telemetry from OpenF1, and supplementary session data from FastF1.
2. **Storage:** raw snapshots saved to `data/raw/` and optionally persisted into PostgreSQL.
3. **Processing:** standardize keys (`season`, `round`, `driver_id`, `constructor_id`), clean missing values, and enforce schema.
4. **Feature engineering:** rolling form, team index, track-specific stats, and qualifying effects.
5. **Modeling:** train Logistic Regression baseline + Random Forest/XGBoost advanced models.
6. **Evaluation:** compare accuracy, precision, recall, and confusion matrix on unseen races.
7. **Visualization/deployment:** Streamlit app for insights and upcoming race predictions.

---

## 4) Student Deliverables (Submission Checklist)

1. **GitHub repository with clean structure** – reproducible, modular project layout.
2. **High-quality README** – setup, architecture, methodology, and outcomes.
3. **API ingestion scripts** – working scripts for Ergast/OpenF1/FastF1 ingestion.
4. **Database schema + instance** – PostgreSQL schema and loaded core tables.
5. **Cleaned dataset** – final modeling table in `data/processed/`.
6. **EDA notebook** – visual exploration of trends and class balance.
7. **Feature pipeline** – script that transforms cleaned data into ML-ready features.
8. **ML models** – at least two trained models with serialized artifacts.
9. **Evaluation report** – metrics and confusion matrix with interpretation.
10. **Streamlit app** – interactive insights + race prediction UI.

---

## 5) Project Structure

```text
formula1-race-prediction-project/
├── app/
│   └── streamlit_app.py
├── artifacts/
│   └── .gitkeep
├── config/
│   └── settings.yaml
├── data/
│   ├── raw/
│   │   └── .gitkeep
│   └── processed/
│       └── .gitkeep
├── notebooks/
│   └── 01_eda.ipynb
├── sql/
│   └── schema_postgres.sql
├── src/
│   ├── ingestion/
│   │   ├── ingest_ergast.py
│   │   ├── ingest_openf1.py
│   │   └── ingest_fastf1.py
│   ├── processing/
│   │   └── clean_data.py
│   ├── features/
│   │   └── build_features.py
│   ├── models/
│   │   ├── train.py
│   │   └── evaluate.py
│   └── utils/
│       ├── io_utils.py
│       └── db.py
├── tests/
│   └── test_features.py
├── requirements.txt
└── README.md
```

---

## 6) Data Ingestion Layer

### What each ingestion script does
- `ingest_ergast.py`: downloads race results, qualifying, lap times for a season range (minimum 2021–2025).
- `ingest_openf1.py`: downloads sessions, laps, and telemetry proxies for selected meeting/session keys.
- `ingest_fastf1.py`: loads race sessions through FastF1 cache and extracts lap-level and weather/session metadata.

### Merge Strategy Across 3 Sources
Use canonical keys:
- `season` + `round`
- `driver_number` / mapped `driver_id`
- `constructor_name` / mapped `constructor_id`
- `session_type` and UTC timestamps

Then build unified tables:
- `results` (historical outcome labels)
- `lap_times` (pace-based signals)
- `telemetry` (speed/throttle/DRS aggregates)

---

## 7) Database Design (PostgreSQL)

Core tables:
- `drivers(driver_id PK, code, given_name, family_name, nationality)`
- `constructors(constructor_id PK, name, nationality)`
- `races(race_id PK, season, round, race_name, circuit_id, race_date)`
- `results(result_id PK, race_id FK, driver_id FK, constructor_id FK, grid, finish_position, points, status)`
- `lap_times(lap_time_id PK, race_id FK, driver_id FK, lap_number, lap_time_ms, sector1_ms, sector2_ms, sector3_ms)`
- `telemetry(telemetry_id PK, race_id FK, driver_id FK, sample_ts, speed, throttle, brake, drs, gear, rpm)`

Relationships:
- one race → many results/laps/telemetry rows
- one driver → many results/laps/telemetry rows
- one constructor → many result rows

---

## 8) Data Processing & Cleaning

1. Standardize naming conventions and IDs.
2. Convert times to milliseconds and timestamps to UTC.
3. Remove duplicates by composite keys (`race_id`, `driver_id`, `lap_number`).
4. Handle missing values:
   - Numeric: median imputation by driver-season or global fallback.
   - Categorical: `"Unknown"` fallback.
5. Normalize/scale continuous model features (for linear models).
6. Validate row-level integrity (one driver per race result label).

---

## 9) Feature Engineering (Critical)

Required features and rationale:
- **Average finishing position:** captures long-term race performance level.
- **Qualifying position:** strongest pre-race proxy for race outcome.
- **Driver consistency score (std of finish positions):** lower variance often correlates with points reliability.
- **Team performance index:** rolling constructor points per race.
- **Recent form (last 3–5 races):** captures current competitiveness.
- **Track-specific performance:** historical finishing/points at same circuit.

Also include:
- median race pace from lap times
- DNF trend
- pit-stop adjusted pace (if available)

---

## 10) Modeling Requirements (Strict)

### Dataset Rules
- Minimum historical window: **3–5 seasons** (recommended 2021–2025).
- One row = one **driver-race** instance.
- Train on past races only; validate on future races (time-aware split).

### Prediction Targets
- Classification target A: `is_top3`
- Classification target B: `is_winner`
- Optional regression target: `points`

### Required Models
1. **Logistic Regression** (baseline)
2. **Random Forest** *or* **XGBoost** (advanced)

### Why these models
- Logistic Regression: interpretable, stable baseline, fast iteration.
- Random Forest: non-linear interactions, robust to feature scales.
- XGBoost: usually strongest tabular performance, handles non-linearity and interactions efficiently.

---

## 11) Evaluation

Required metrics:
- Accuracy
- Precision / Recall
- Confusion Matrix

Interpretation guidance:
- For podium prediction, recall tells how many true podium drivers were captured.
- Precision shows false-positive control (important for high-confidence picks).
- Confusion matrix highlights class imbalance issues and threshold trade-offs.

---

## 12) Deployment (Streamlit)

App requirements:
- show driver/team form and trend charts
- allow race selection and generate predicted top 3 probabilities
- display model confidence and key feature contributions (optional SHAP)

Run locally:
```bash
streamlit run app/streamlit_app.py
```

---

## 13) Quickstart

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python src/ingestion/ingest_ergast.py --start-season 2021 --end-season 2025
python src/ingestion/ingest_openf1.py --year 2026
python src/ingestion/ingest_fastf1.py --year 2025 --session R

python src/processing/clean_data.py
python src/features/build_features.py
python src/models/train.py --target is_top3
python src/models/evaluate.py --target is_top3

streamlit run app/streamlit_app.py
```

---

## 14) Bonus (Advanced Students)

- Real-time prediction refresh as live sessions update through OpenF1.
- Airflow DAG for scheduled ingestion, feature generation, training, and scoring.
- Live cloud dashboard (Streamlit Community Cloud / containerized deployment).

---

## 15) Portfolio Impact

This project demonstrates practical engineering + modeling maturity:
- API orchestration
- data quality handling
- supervised ML with evaluation rigor
- deployable analytics application

That combination is exactly what hiring managers expect in junior-to-mid data roles.
