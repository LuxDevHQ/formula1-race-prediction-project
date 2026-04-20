"""Feature engineering for driver-race level supervised learning table."""

import pandas as pd
from src.utils.io_utils import save_parquet


def main() -> None:
    df = pd.read_parquet("data/processed/cleaned_results.parquet")
    df = df.sort_values(["driver_id", "season", "round"])  # preserve race chronology

    # Targets
    df["is_winner"] = (df["finish_position"] == 1).astype(int)
    df["is_top3"] = (df["finish_position"] <= 3).astype(int)

    # Rolling features
    df["avg_finish_pos"] = (
        df.groupby("driver_id")["finish_position"].transform(lambda s: s.shift(1).rolling(5, min_periods=1).mean())
    )
    df["recent_form_points"] = (
        df.groupby("driver_id")["points"].transform(lambda s: s.shift(1).rolling(3, min_periods=1).mean())
    )
    df["consistency_score"] = (
        df.groupby("driver_id")["finish_position"].transform(lambda s: s.shift(1).rolling(5, min_periods=2).std())
    )

    # Team index proxy from constructor points trend
    df["team_performance_index"] = (
        df.groupby("constructor_id")["points"].transform(lambda s: s.shift(1).rolling(5, min_periods=1).mean())
    )

    # Track-specific performance proxy
    df["track_perf"] = (
        df.groupby(["driver_id", "race_name"])["finish_position"]
        .transform(lambda s: s.shift(1).rolling(3, min_periods=1).mean())
    )

    df["qualifying_position"] = df["grid"]

    feature_cols = [
        "season",
        "round",
        "driver_id",
        "constructor_id",
        "qualifying_position",
        "avg_finish_pos",
        "recent_form_points",
        "consistency_score",
        "team_performance_index",
        "track_perf",
        "points",
        "is_top3",
        "is_winner",
    ]

    model_df = df[feature_cols].fillna(df[feature_cols].median(numeric_only=True))
    save_parquet(model_df, "data/processed/model_table.parquet")
    print(f"Saved model table with {len(model_df)} rows")


if __name__ == "__main__":
    main()
