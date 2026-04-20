"""Ingest race session data using FastF1.

Usage:
python src/ingestion/ingest_fastf1.py --year 2025 --session R
"""

import argparse
import fastf1
import pandas as pd
from src.utils.io_utils import save_csv


def main(year: int, session_type: str) -> None:
    fastf1.Cache.enable_cache("data/raw/fastf1_cache")

    event_schedule = fastf1.get_event_schedule(year)
    rows = []
    for _, event in event_schedule.iterrows():
        try:
            session = fastf1.get_session(year, event["EventName"], session_type)
            session.load(laps=True, telemetry=False, weather=True)
            laps = session.laps[["Driver", "LapNumber", "LapTime", "Compound", "Stint"]].copy()
            laps["season"] = year
            laps["event_name"] = event["EventName"]
            rows.append(laps)
        except Exception as exc:  # keep pipeline resilient for missing sessions
            print(f"Skipping {event['EventName']}: {exc}")

    all_laps = pd.concat(rows, ignore_index=True) if rows else pd.DataFrame()
    save_csv(all_laps, "data/raw/fastf1_laps.csv")
    print(f"Saved {len(all_laps)} FastF1 lap rows")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--year", type=int, required=True)
    parser.add_argument("--session", type=str, default="R")
    args = parser.parse_args()
    main(args.year, args.session)
