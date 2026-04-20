"""Ingest historical F1 data from Ergast API.

Usage:
python src/ingestion/ingest_ergast.py --start-season 2021 --end-season 2025
"""

import argparse
import requests
import pandas as pd
from src.utils.io_utils import save_csv

ERGAST_BASE = "https://ergast.com/api/f1"


def fetch_json(url: str) -> dict:
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    return response.json()


def fetch_results_for_season(season: int) -> pd.DataFrame:
    data = fetch_json(f"{ERGAST_BASE}/{season}/results.json?limit=2000")
    races = data["MRData"]["RaceTable"]["Races"]
    rows = []
    for race in races:
        for r in race.get("Results", []):
            rows.append(
                {
                    "season": int(race["season"]),
                    "round": int(race["round"]),
                    "race_name": race["raceName"],
                    "race_date": race["date"],
                    "driver_id": r["Driver"]["driverId"],
                    "constructor_id": r["Constructor"]["constructorId"],
                    "grid": int(r["grid"]),
                    "finish_position": int(r.get("position", 0) or 0),
                    "points": float(r.get("points", 0.0)),
                    "status": r["status"],
                }
            )
    return pd.DataFrame(rows)


def main(start_season: int, end_season: int) -> None:
    frames = [fetch_results_for_season(year) for year in range(start_season, end_season + 1)]
    results = pd.concat(frames, ignore_index=True)
    save_csv(results, "data/raw/ergast_results.csv")
    print(f"Saved {len(results)} Ergast result rows to data/raw/ergast_results.csv")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--start-season", type=int, required=True)
    parser.add_argument("--end-season", type=int, required=True)
    args = parser.parse_args()
    main(args.start_season, args.end_season)
