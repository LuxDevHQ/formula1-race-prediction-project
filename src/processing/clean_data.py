"""Clean and merge raw F1 data from Ergast, OpenF1, and FastF1."""

import pandas as pd
from src.utils.io_utils import save_parquet


def main() -> None:
    ergast = pd.read_csv("data/raw/ergast_results.csv")

    # Optional data sources (pipeline still runs if missing)
    try:
        openf1_laps = pd.read_csv("data/raw/openf1_laps.csv")
    except FileNotFoundError:
        openf1_laps = pd.DataFrame()

    try:
        fastf1_laps = pd.read_csv("data/raw/fastf1_laps.csv")
    except FileNotFoundError:
        fastf1_laps = pd.DataFrame()

    # Basic cleaning
    ergast = ergast.drop_duplicates(subset=["season", "round", "driver_id"])
    ergast["finish_position"] = ergast["finish_position"].replace(0, pd.NA)
    ergast["finish_position"] = ergast["finish_position"].fillna(ergast["finish_position"].median())

    # Optional pace proxy from OpenF1 laps when available
    if not openf1_laps.empty and "lap_duration" in openf1_laps.columns and "driver_number" in openf1_laps.columns:
        pace = (
            openf1_laps.groupby("driver_number", as_index=False)["lap_duration"]
            .median()
            .rename(columns={"driver_number": "driver_number_openf1", "lap_duration": "median_openf1_lap"})
        )
        ergast = ergast.merge(pace, how="left", left_on="grid", right_on="driver_number_openf1")

    # FastF1 aggregate
    if not fastf1_laps.empty and "Driver" in fastf1_laps.columns:
        fast_agg = (
            fastf1_laps.groupby("Driver", as_index=False)["LapNumber"]
            .count()
            .rename(columns={"Driver": "driver_code", "LapNumber": "fastf1_lap_count"})
        )
        ergast = ergast.merge(fast_agg, how="left", left_on="driver_id", right_on="driver_code")

    save_parquet(ergast, "data/processed/cleaned_results.parquet")
    print(f"Saved cleaned dataset with {len(ergast)} rows")


if __name__ == "__main__":
    main()
