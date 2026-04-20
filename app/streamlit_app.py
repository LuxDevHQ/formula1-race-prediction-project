"""Streamlit dashboard for F1 insights and predictions."""

from pathlib import Path
import joblib
import pandas as pd
import streamlit as st

st.set_page_config(page_title="F1 Race Prediction", layout="wide")
st.title("🏎️ F1 2026 Race Prediction Dashboard")

model_table_path = Path("data/processed/model_table.parquet")
if not model_table_path.exists():
    st.warning("Run processing + feature scripts first to generate data/processed/model_table.parquet")
    st.stop()

_df = pd.read_parquet(model_table_path)
st.subheader("Dataset Snapshot")
st.dataframe(_df.head(20), use_container_width=True)

st.subheader("Driver Form Overview")
form_df = _df.groupby("driver_id", as_index=False)["recent_form_points"].mean().sort_values("recent_form_points", ascending=False)
st.bar_chart(form_df.set_index("driver_id").head(10))

st.subheader("Prediction")
model_path = Path("artifacts/rf_is_top3.pkl")
if not model_path.exists():
    st.info("Train a model first: python src/models/train.py --target is_top3")
else:
    model = joblib.load(model_path)
    latest = _df.sort_values(["season", "round"]).groupby("driver_id").tail(1).copy()
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
    probs = model.predict_proba(latest[feature_cols])[:, 1]
    latest["top3_probability"] = probs
    st.dataframe(latest[["driver_id", "constructor_id", "top3_probability"]].sort_values("top3_probability", ascending=False).head(10))
