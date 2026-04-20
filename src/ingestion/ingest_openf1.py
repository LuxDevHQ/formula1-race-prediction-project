"""Ingest session and lap-level data from OpenF1 API.

Usage:
python src/ingestion/ingest_openf1.py --year 2026
"""

import argparse
import requests
import pandas as pd
from src.utils.io_utils import save_csv

OPENF1_BASE = "https://api.openf1.org/v1"


def fetch(endpoint: str, params: dict) -> list:
    response = requests.get(f"{OPENF1_BASE}/{endpoint}", params=params, timeout=30)
    response.raise_for_status()
    return response.json()


def main(year: int) -> None:
    sessions = pd.DataFrame(fetch("sessions", {"year": year}))
    save_csv(sessions, "data/raw/openf1_sessions.csv")

    # Pull lap rows for first N sessions to keep ingestion small for beginners.
    lap_frames = []
    for session_key in sessions.get("session_key", pd.Series(dtype=int)).head(10).tolist():
        laps = fetch("laps", {"session_key": session_key})
        if laps:
            lap_frames.append(pd.DataFrame(laps))

    laps_df = pd.concat(lap_frames, ignore_index=True) if lap_frames else pd.DataFrame()
    save_csv(laps_df, "data/raw/openf1_laps.csv")

    print(f"Saved {len(sessions)} OpenF1 sessions and {len(laps_df)} lap rows")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--year", type=int, default=2026)
    args = parser.parse_args()
    main(args.year)
