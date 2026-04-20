"""Train baseline and advanced ML models for F1 predictions."""

import argparse
import os
import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
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

    numeric_features = [
        "season",
        "round",
        "qualifying_position",
        "avg_finish_pos",
        "recent_form_points",
        "consistency_score",
        "team_performance_index",
        "track_perf",
    ]
    categorical_features = ["driver_id", "constructor_id"]

    preprocess = ColumnTransformer(
        transformers=[
            (
                "num",
                Pipeline([
                    ("imputer", SimpleImputer(strategy="median")),
                    ("scaler", StandardScaler()),
                ]),
                numeric_features,
            ),
            (
                "cat",
                Pipeline([
                    ("imputer", SimpleImputer(strategy="most_frequent")),
                    ("encoder", OneHotEncoder(handle_unknown="ignore")),
                ]),
                categorical_features,
            ),
        ]
    )

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    models = {
        "logreg": LogisticRegression(max_iter=1000, class_weight="balanced"),
        "rf": RandomForestClassifier(n_estimators=400, random_state=42, class_weight="balanced"),
    }

    os.makedirs("artifacts", exist_ok=True)
    for name, estimator in models.items():
        pipeline = Pipeline([("preprocess", preprocess), ("model", estimator)])
        pipeline.fit(X_train, y_train)
        joblib.dump(pipeline, f"artifacts/{name}_{target}.pkl")
        print(f"Saved artifacts/{name}_{target}.pkl")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", type=str, default="is_top3", choices=["is_top3", "is_winner"])
    args = parser.parse_args()
    main(args.target)
