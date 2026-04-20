"""Evaluate trained model artifacts."""

import argparse
import glob
import json
import os
import joblib
import pandas as pd
from sklearn.metrics import accuracy_score, precision_score, recall_score, confusion_matrix
from sklearn.model_selection import train_test_split


def main(target: str) -> None:
    df = pd.read_parquet("data/processed/model_table.parquet")
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
    ]

    X = df[feature_cols]
    y = df[target]
    _, X_test, _, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    os.makedirs("artifacts/metrics", exist_ok=True)
    for model_path in glob.glob(f"artifacts/*_{target}.pkl"):
        model = joblib.load(model_path)
        preds = model.predict(X_test)
        metrics = {
            "accuracy": accuracy_score(y_test, preds),
            "precision": precision_score(y_test, preds, zero_division=0),
            "recall": recall_score(y_test, preds, zero_division=0),
            "confusion_matrix": confusion_matrix(y_test, preds).tolist(),
        }
        name = os.path.basename(model_path).replace(".pkl", "")
        with open(f"artifacts/metrics/{name}.json", "w", encoding="utf-8") as f:
            json.dump(metrics, f, indent=2)
        print(f"Saved artifacts/metrics/{name}.json")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", type=str, default="is_top3", choices=["is_top3", "is_winner"])
    args = parser.parse_args()
    main(args.target)
